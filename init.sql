-- =============================================================================
-- init.sql — AuditChain Database Schema
-- Compatible con PostgreSQL 16
-- Ejecutar: docker-compose down -v && docker-compose up db
-- =============================================================================

-- =============================================================================
-- BLOQUE 1: SCHEMA + EXTENSIONES + ENUMS
-- =============================================================================

DROP SCHEMA IF EXISTS auditchain CASCADE;
CREATE SCHEMA auditchain;

SET search_path TO auditchain, public;

-- Extensiones
CREATE EXTENSION IF NOT EXISTS pgcrypto;   -- gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS citext;     -- email case-insensitive
CREATE EXTENSION IF NOT EXISTS pg_trgm;   -- búsqueda fuzzy
CREATE EXTENSION IF NOT EXISTS unaccent;  -- búsqueda sin tildes

-- ENUMs nativos
CREATE TYPE auditchain.enum_rol_usuario AS ENUM (
    'admin',
    'auditor'
);

CREATE TYPE auditchain.enum_estado_auditoria AS ENUM (
    'pendiente',
    'completada',
    'con_observaciones',
    'vencida'
);

-- [FIN BLOQUE 1: SCHEMA + EXTENSIONES + ENUMS]

-- =============================================================================
-- BLOQUE 2: TABLA USUARIOS
-- =============================================================================

CREATE TABLE auditchain.usuarios (
    id             UUID        NOT NULL DEFAULT gen_random_uuid(),
    nombre         VARCHAR(200) NOT NULL,
    email          CITEXT      NOT NULL,
    password_hash  TEXT        NOT NULL,
    rol            auditchain.enum_rol_usuario NOT NULL DEFAULT 'auditor',
    activo         BOOLEAN     NOT NULL DEFAULT true,
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT now(),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT pk_usuarios                 PRIMARY KEY (id),
    CONSTRAINT uq_usuarios_email           UNIQUE (email),
    CONSTRAINT ck_usuarios_nombre_no_vacio CHECK (nombre <> '')
);

CREATE INDEX ix_usuarios_rol ON auditchain.usuarios (rol);

-- [FIN BLOQUE 2: TABLA USUARIOS]

-- =============================================================================
-- BLOQUE 3: TABLAS SUCURSALES + AUDITORES
-- =============================================================================

CREATE TABLE auditchain.sucursales (
    id               UUID         NOT NULL DEFAULT gen_random_uuid(),
    nombre           VARCHAR(200) NOT NULL,
    region           VARCHAR(100) NOT NULL,
    direccion        TEXT,
    puntaje_promedio NUMERIC(5,2)          DEFAULT 0.00,
    activo           BOOLEAN      NOT NULL DEFAULT true,
    creado_en        TIMESTAMPTZ  NOT NULL DEFAULT now(),
    actualizado_en   TIMESTAMPTZ  NOT NULL DEFAULT now(),

    CONSTRAINT pk_sucursales                  PRIMARY KEY (id),
    CONSTRAINT ck_sucursales_nombre_no_vacio  CHECK (nombre <> ''),
    CONSTRAINT ck_sucursales_puntaje_rango    CHECK (puntaje_promedio BETWEEN 0.00 AND 100.00)
);

CREATE INDEX ix_sucursales_region ON auditchain.sucursales (region);
CREATE INDEX ix_sucursales_activo ON auditchain.sucursales (activo);

-- -----------------------------------------------------------------------------

CREATE TABLE auditchain.auditores (
    id             UUID         NOT NULL DEFAULT gen_random_uuid(),
    usuario_id     UUID         NOT NULL,
    nombre         VARCHAR(200) NOT NULL,
    email          CITEXT       NOT NULL,
    region         VARCHAR(100),
    activo         BOOLEAN      NOT NULL DEFAULT true,
    creado_en      TIMESTAMPTZ  NOT NULL DEFAULT now(),
    actualizado_en TIMESTAMPTZ  NOT NULL DEFAULT now(),

    CONSTRAINT pk_auditores                     PRIMARY KEY (id),
    CONSTRAINT uq_auditores_email               UNIQUE (email),
    CONSTRAINT fk_auditores_usuario_id_usuarios FOREIGN KEY (usuario_id)
        REFERENCES auditchain.usuarios (id) ON DELETE RESTRICT
);

CREATE INDEX ix_auditores_usuario_id ON auditchain.auditores (usuario_id);
CREATE INDEX ix_auditores_region     ON auditchain.auditores (region);

-- [FIN BLOQUE 3: TABLAS SUCURSALES + AUDITORES]

-- =============================================================================
-- BLOQUE 4: TABLA AUDITORIAS + FUNCIONES + TRIGGERS
-- =============================================================================

CREATE TABLE auditchain.auditorias (
    id                UUID         NOT NULL DEFAULT gen_random_uuid(),
    sucursal_id       UUID         NOT NULL,
    auditor_id        UUID         NOT NULL,
    fecha_programada  TIMESTAMPTZ  NOT NULL,
    fecha_realizada   TIMESTAMPTZ,
    puntaje           NUMERIC(5,2),
    estado            auditchain.enum_estado_auditoria NOT NULL DEFAULT 'pendiente',
    observaciones     TEXT,
    creado_en         TIMESTAMPTZ  NOT NULL DEFAULT now(),
    actualizado_en    TIMESTAMPTZ  NOT NULL DEFAULT now(),

    CONSTRAINT pk_auditorias                        PRIMARY KEY (id),
    CONSTRAINT fk_auditorias_sucursal_id_sucursales FOREIGN KEY (sucursal_id)
        REFERENCES auditchain.sucursales (id) ON DELETE RESTRICT,
    CONSTRAINT fk_auditorias_auditor_id_auditores   FOREIGN KEY (auditor_id)
        REFERENCES auditchain.auditores (id) ON DELETE RESTRICT,
    CONSTRAINT ck_auditorias_puntaje_rango          CHECK (puntaje BETWEEN 0.00 AND 100.00)
);

CREATE INDEX ix_auditorias_sucursal_id      ON auditchain.auditorias (sucursal_id);
CREATE INDEX ix_auditorias_auditor_id       ON auditchain.auditorias (auditor_id);
CREATE INDEX ix_auditorias_estado           ON auditchain.auditorias (estado);
CREATE INDEX ix_auditorias_fecha_programada ON auditchain.auditorias (fecha_programada);
CREATE INDEX ix_auditorias_sucursal_estado  ON auditchain.auditorias (sucursal_id, estado);

-- -----------------------------------------------------------------------------
-- FUNCIÓN + TRIGGERS: actualizado_en automático
-- -----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION auditchain.actualizar_timestamp()
RETURNS TRIGGER
LANGUAGE plpgsql AS $$
BEGIN
    NEW.actualizado_en = now();
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_actualizar_ts_usuarios
    BEFORE UPDATE ON auditchain.usuarios
    FOR EACH ROW EXECUTE FUNCTION auditchain.actualizar_timestamp();

CREATE TRIGGER trg_actualizar_ts_sucursales
    BEFORE UPDATE ON auditchain.sucursales
    FOR EACH ROW EXECUTE FUNCTION auditchain.actualizar_timestamp();

CREATE TRIGGER trg_actualizar_ts_auditores
    BEFORE UPDATE ON auditchain.auditores
    FOR EACH ROW EXECUTE FUNCTION auditchain.actualizar_timestamp();

CREATE TRIGGER trg_actualizar_ts_auditorias
    BEFORE UPDATE ON auditchain.auditorias
    FOR EACH ROW EXECUTE FUNCTION auditchain.actualizar_timestamp();

-- -----------------------------------------------------------------------------
-- FUNCIÓN + TRIGGER: recalcular puntaje_promedio en sucursales
-- -----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION auditchain.recalcular_puntaje_sucursal()
RETURNS TRIGGER
LANGUAGE plpgsql AS $$
DECLARE
    v_sucursal_id UUID;
BEGIN
    -- En DELETE solo existe OLD; en INSERT/UPDATE solo existe NEW
    v_sucursal_id := COALESCE(NEW.sucursal_id, OLD.sucursal_id);

    UPDATE auditchain.sucursales
    SET puntaje_promedio = (
        SELECT COALESCE(AVG(puntaje), 0.00)
        FROM auditchain.auditorias
        WHERE sucursal_id = v_sucursal_id
          AND estado IN ('completada', 'con_observaciones')
          AND puntaje IS NOT NULL
    )
    WHERE id = v_sucursal_id;

    RETURN NULL;  -- AFTER trigger: valor de retorno ignorado
END;
$$;

CREATE TRIGGER trg_puntaje_sucursal
    AFTER INSERT OR UPDATE OR DELETE ON auditchain.auditorias
    FOR EACH ROW EXECUTE FUNCTION auditchain.recalcular_puntaje_sucursal();

-- [FIN BLOQUE 4: TABLA AUDITORIAS + FUNCIONES + TRIGGERS]
