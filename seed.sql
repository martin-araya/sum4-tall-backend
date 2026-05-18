-- =============================================================================
-- seed.sql — datos de prueba para desarrollo
-- Ejecutar: docker-compose exec -T db psql -U postgres -d auditchain_db < db/seed.sql
-- =============================================================================

SET search_path TO auditchain, public;

DO $$
DECLARE
    -- Usuarios
    v_admin_id         UUID := gen_random_uuid();
    v_auditor_id       UUID := gen_random_uuid();

    -- Sucursales
    v_suc_metro_id     UUID := gen_random_uuid();
    v_suc_valpo_id     UUID := gen_random_uuid();
    v_suc_biobio_id    UUID := gen_random_uuid();
    v_suc_arau_id      UUID := gen_random_uuid();

    -- Auditores
    v_aud_valentina_id UUID := gen_random_uuid();
    v_aud_rodrigo_id   UUID := gen_random_uuid();

    -- Auditorías
    v_audit1_id        UUID := gen_random_uuid();
    v_audit2_id        UUID := gen_random_uuid();
    v_audit3_id        UUID := gen_random_uuid();
    v_audit4_id        UUID := gen_random_uuid();
    v_audit5_id        UUID := gen_random_uuid();
    v_audit6_id        UUID := gen_random_uuid();
    v_audit7_id        UUID := gen_random_uuid();
    v_audit8_id        UUID := gen_random_uuid();

BEGIN

    -- =========================================================================
    -- USUARIOS
    -- =========================================================================
    INSERT INTO auditchain.usuarios (id, nombre, email, password_hash, rol) VALUES
        (v_admin_id,
         'Administrador Sistema',
         'admin@auditchain.cl',
         crypt('admin123', gen_salt('bf')),
         'admin'),
        (v_auditor_id,
         'Auditor Base',
         'auditor@auditchain.cl',
         crypt('auditor123', gen_salt('bf')),
         'auditor');

    -- =========================================================================
    -- SUCURSALES
    -- =========================================================================
    INSERT INTO auditchain.sucursales (id, nombre, region, direccion) VALUES
        (v_suc_metro_id,
         'Sucursal Santiago Centro',
         'Metropolitana',
         'Av. Libertador Bernardo O''Higgins 1234, Santiago'),
        (v_suc_valpo_id,
         'Sucursal Viña del Mar',
         'Valparaíso',
         'Av. San Martín 456, Viña del Mar'),
        (v_suc_biobio_id,
         'Sucursal Concepción',
         'Biobío',
         'Av. Los Carrera 789, Concepción'),
        (v_suc_arau_id,
         'Sucursal Temuco',
         'La Araucanía',
         'Av. Caupolicán 321, Temuco');

    -- =========================================================================
    -- AUDITORES (ambos vinculados al usuario auditor)
    -- =========================================================================
    INSERT INTO auditchain.auditores (id, usuario_id, nombre, email, region) VALUES
        (v_aud_valentina_id,
         v_auditor_id,
         'Valentina Lagos',
         'valentina.lagos@auditchain.cl',
         'Valparaíso'),
        (v_aud_rodrigo_id,
         v_auditor_id,
         'Rodrigo Muñoz',
         'rodrigo.munoz@auditchain.cl',
         'Metropolitana');

    -- =========================================================================
    -- AUDITORÍAS
    -- =========================================================================

    -- 3 completadas
    INSERT INTO auditchain.auditorias
        (id, sucursal_id, auditor_id, fecha_programada, fecha_realizada, puntaje, estado)
    VALUES
        (v_audit1_id,
         v_suc_valpo_id, v_aud_valentina_id,
         '2026-03-10 09:00:00+00', '2026-03-10 11:30:00+00',
         92.00, 'completada'),
        (v_audit2_id,
         v_suc_metro_id, v_aud_rodrigo_id,
         '2026-03-20 10:00:00+00', '2026-03-20 12:45:00+00',
         78.00, 'completada'),
        (v_audit3_id,
         v_suc_biobio_id, v_aud_valentina_id,
         '2026-04-05 09:00:00+00', '2026-04-05 11:00:00+00',
         85.00, 'completada');

    -- 2 pendientes (fecha_programada futura, sin puntaje)
    INSERT INTO auditchain.auditorias
        (id, sucursal_id, auditor_id, fecha_programada, estado)
    VALUES
        (v_audit4_id,
         v_suc_arau_id, v_aud_rodrigo_id,
         '2026-06-01 09:00:00+00', 'pendiente'),
        (v_audit5_id,
         v_suc_metro_id, v_aud_valentina_id,
         '2026-06-15 10:00:00+00', 'pendiente');

    -- 2 con observaciones
    INSERT INTO auditchain.auditorias
        (id, sucursal_id, auditor_id, fecha_programada, fecha_realizada, puntaje, estado, observaciones)
    VALUES
        (v_audit6_id,
         v_suc_valpo_id, v_aud_rodrigo_id,
         '2026-04-18 09:00:00+00', '2026-04-18 12:00:00+00',
         65.00, 'con_observaciones',
         'Deficiencias en control de temperatura de cámara frigorífica. Requiere corrección en 15 días.'),
        (v_audit7_id,
         v_suc_arau_id, v_aud_valentina_id,
         '2026-04-28 09:00:00+00', '2026-04-28 11:30:00+00',
         71.00, 'con_observaciones',
         'Documentación de proveedores incompleta. Personal no certificado en manipulación de alimentos.');

    -- 1 vencida (fecha_programada en el pasado, sin fecha_realizada)
    INSERT INTO auditchain.auditorias
        (id, sucursal_id, auditor_id, fecha_programada, estado, observaciones)
    VALUES
        (v_audit8_id,
         v_suc_biobio_id, v_aud_rodrigo_id,
         '2026-05-05 09:00:00+00', 'vencida',
         'Auditoría no realizada dentro del plazo establecido.');

END;
$$;

SELECT COUNT(*) AS total_auditorias FROM auditchain.auditorias;
