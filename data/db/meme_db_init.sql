/*Used to instantiate the database the first time*/
CREATE TABLE IF NOT EXISTS pending_meme
(
  user_id varchar(20) NOT NULL,
  u_message_id varchar(25) NOT NULL,
  g_message_id varchar(25) NOT NULL,
  group_id varchar(20) NOT NULL,
  PRIMARY KEY (group_id, g_message_id)
);
-----
CREATE TABLE IF NOT EXISTS published_meme
(
  channel_id varchar(25) NOT NULL,
  c_message_id varchar(25) NOT NULL,
  PRIMARY KEY (channel_id, c_message_id)
);
-----
CREATE TABLE IF NOT EXISTS votes
(
  user_id varchar(20) NOT NULL,
  c_message_id varchar(25) NOT NULL,
  channel_id varchar(20) NOT NULL,
  is_upvote boolean NOT NULL,
  PRIMARY KEY (user_id, c_message_id, channel_id),
  FOREIGN KEY (c_message_id, channel_id) REFERENCES published_meme (c_message_id, channel_id) ON DELETE CASCADE ON UPDATE CASCADE
);
-----
CREATE TABLE IF NOT EXISTS admin_votes
(
  admin_id varchar(20) NOT NULL,
  g_message_id varchar(25) NOT NULL,
  group_id varchar(20) NOT NULL,
  is_upvote boolean NOT NULL,
  PRIMARY KEY (admin_id, g_message_id, group_id),
  FOREIGN KEY (g_message_id, group_id) REFERENCES pending_meme (g_message_id, group_id) ON DELETE CASCADE ON UPDATE CASCADE
);
-----
CREATE TABLE IF NOT EXISTS credited_users
(
  user_id varchar(20) NOT NULL,
  PRIMARY KEY (user_id)
);
-----
CREATE TABLE IF NOT EXISTS banned_users
(
  user_id varchar(20) NOT NULL,
  PRIMARY KEY (user_id)
);
/*
CREATE VIEW approved AS
    SELECT COUNT(is_upvote) as number, a_group_id, a_message_id 
    FROM admin_votes
    WHERE is_upvote = true
    GROUP BY group_id, g_message_id;
*/
