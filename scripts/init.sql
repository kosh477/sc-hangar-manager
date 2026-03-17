INSERT INTO users (id, name, email, login, password)
VALUES (1, 'Demo Pilot', 'pilot@hangar.local', 'pilot', '$2b$12$Zm8vLQ73Lb0P6x2ubfI5H.VR6/BsENv9xR6dJ79Lh2pgrdcQ6chSe')
ON DUPLICATE KEY UPDATE
name = VALUES(name),
email = VALUES(email),
login = VALUES(login),
password = VALUES(password);

INSERT INTO ships (id, vendor, model, name)
VALUES
  (1, 'Aegis Dynamics', 'Avenger Titan', 'Titan One'),
  (2, 'Drake Interplanetary', 'Cutlass Black', 'Cargo Crow')
ON DUPLICATE KEY UPDATE
vendor = VALUES(vendor),
model = VALUES(model),
name = VALUES(name);

INSERT INTO partsTypes (id, type, isReplaceble)
VALUES
  (1, 'Power Plant', 1),
  (2, 'Shield Generator', 1),
  (3, 'Cooler', 1)
ON DUPLICATE KEY UPDATE
type = VALUES(type),
isReplaceble = VALUES(isReplaceble);

INSERT INTO shipsParts (id, vendor, model, class, size, partTypeId)
VALUES
  (1, 'JS-300', 'Power Cell', 'Military', 1, 1),
  (2, 'Aegis', 'Bulwark', 'Military', 2, 2),
  (3, 'Klaus & Werner', 'Frost-Star', 'Civilian', 1, 3),
  (4, 'Hurston Dynamics', 'Havoc', 'Competition', 2, 1),
  (5, 'Shubin', 'Defender', 'Industrial', 2, 2)
ON DUPLICATE KEY UPDATE
vendor = VALUES(vendor),
model = VALUES(model),
class = VALUES(class),
size = VALUES(size),
partTypeId = VALUES(partTypeId);

INSERT INTO shipsByUser (id, userId, shipId, isDeleted)
VALUES
  (1, 1, 1, 0),
  (2, 1, 2, 0)
ON DUPLICATE KEY UPDATE
userId = VALUES(userId),
shipId = VALUES(shipId),
isDeleted = VALUES(isDeleted);

INSERT INTO partsByUser (id, partId, userId, isDeleted)
VALUES
  (1, 1, 1, 0),
  (2, 2, 1, 0),
  (3, 3, 1, 0),
  (4, 4, 1, 0),
  (5, 5, 1, 0)
ON DUPLICATE KEY UPDATE
partId = VALUES(partId),
userId = VALUES(userId),
isDeleted = VALUES(isDeleted);

INSERT INTO partsByShip (id, partId, shipId)
VALUES
  (1, 1, 1),
  (2, 2, 1),
  (3, 3, 1),
  (4, 4, 2),
  (5, 5, 2)
ON DUPLICATE KEY UPDATE
partId = VALUES(partId),
shipId = VALUES(shipId);
