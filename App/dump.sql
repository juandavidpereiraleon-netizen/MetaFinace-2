BEGIN TRANSACTION;
CREATE TABLE ahorros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meta_id INTEGER,
            usuario_id INTEGER,
            cantidad REAL,
            fecha TEXT,
            FOREIGN KEY (meta_id) REFERENCES metas(id) ON DELETE CASCADE,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        );
INSERT INTO "ahorros" VALUES(1,1,1,200.0,'16/09/2025');
CREATE TABLE aportes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            curso TEXT,
            cantidad REAL,
            fecha TEXT,
            hora TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        );
CREATE TABLE ascensos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            curso_anterior TEXT,
            curso_nuevo TEXT,
            fecha TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        );
CREATE TABLE metas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            curso TEXT,
            nombre TEXT,
            fecha TEXT,
            costo REAL
        );
INSERT INTO "metas" VALUES(1,'11','Viaje fin de curso','31/12/2025',1000.0);
CREATE TABLE salidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meta_id INTEGER,
            usuario_id INTEGER,
            cantidad REAL,
            fecha TEXT,
            FOREIGN KEY (meta_id) REFERENCES metas(id) ON DELETE CASCADE,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        );
INSERT INTO "salidas" VALUES(1,1,1,50.0,'16/09/2025');
CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            padre TEXT,
            estudiante TEXT,
            curso TEXT,
            promocion TEXT,
            correo TEXT UNIQUE,
            contrasena TEXT,
            tipo_usuario TEXT DEFAULT 'user'
        );
INSERT INTO "usuarios" VALUES(1,'-','-','-','-','juan.david.pereira.leon@gmail.com','7719','admin');
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('usuarios',3);
INSERT INTO "sqlite_sequence" VALUES('metas',1);
INSERT INTO "sqlite_sequence" VALUES('ahorros',1);
INSERT INTO "sqlite_sequence" VALUES('salidas',1);
COMMIT;
