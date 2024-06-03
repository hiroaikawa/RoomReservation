CREATE TABLE trn_meeting 
(id INT NOT NULL AUTO_INCREMENT,
room_id INT NOT NULL, 
user_id INT NOT NULL,
name TEXT NOT NULL,
start_time DATETIME NOT NULL,
end_time DATETIME NOT NULL,
comment TEXT,
created_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
modified_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

PRIMARY KEY (id),
CONSTRAINT c_start_end CHECK (start_time <= end_time),
FOREIGN KEY fk_trn_meeting_room_id (room_id) references mas_room(id) on delete cascade,
FOREIGN KEY fk_trn_meeting_user_id (user_id) references mas_user(id)),

DEFAULT CHARSET=utf8;