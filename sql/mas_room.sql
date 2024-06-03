CREATE TABLE mas_room 
(id INT NOT NULL AUTO_INCREMENT, 
room_group_id INT NOT NULL, 
name TEXT NOT NULL,
created_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
modified_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
PRIMARY KEY (id),
FOREIGN KEY fk_mas_room_room_group_id (room_group_id) references mas_room_group(id) on delete cascade)
DEFAULT CHARSET=utf8;