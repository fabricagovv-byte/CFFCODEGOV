CREATE TABLE campaigns_antiga (id INTEGER PRIMARY KEY, name TEXT NOT NULL, objective TEXT NOT NULL, channel_id INTEGER, starts_on TEXT, ends_on TEXT, status TEXT DEFAULT 'PLANEJADA', owner_id INTEGER NOT NULL, created_at TEXT NOT NULL, FOREIGN KEY(owner_id) REFERENCES users(id));
INSERT INTO campaigns_antiga SELECT id,name,objective,channel_id,starts_on,ends_on,status,owner_id,created_at FROM campaigns;
DROP TABLE campaigns;
ALTER TABLE campaigns_antiga RENAME TO campaigns;
