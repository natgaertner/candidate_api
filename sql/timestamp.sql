ALTER TABLE contest 
ADD updated TIMESTAMP;

ALTER TABLE contest 
ALTER COLUMN updated 
SET DEFAULT CURRENT_TIMESTAMP;

UPDATE contest
SET updated=CURRENT_TIMESTAMP;

CREATE OR REPLACE FUNCTION update_updated_column()
RETURNS TRIGGER AS '
BEGIN
	NEW.updated = NOW();
	RETURN NEW;
		END;
		' LANGUAGE 'plpgsql';

		CREATE TRIGGER update_updated_modtime BEFORE UPDATE
		ON contest FOR EACH ROW EXECUTE PROCEDURE
		update_updated_column();

ALTER TABLE candidate 
ADD updated TIMESTAMP;

ALTER TABLE candidate 
ALTER COLUMN updated 
SET DEFAULT CURRENT_TIMESTAMP;

UPDATE candidate 
SET updated=CURRENT_TIMESTAMP;

CREATE OR REPLACE FUNCTION update_updated_column()
RETURNS TRIGGER AS '
BEGIN
	NEW.updated = NOW();
	RETURN NEW;
		END;
		' LANGUAGE 'plpgsql';

		CREATE TRIGGER update_updated_modtime BEFORE UPDATE
		ON candidate FOR EACH ROW EXECUTE PROCEDURE
		update_updated_column();
    
ALTER TABLE electoral_district 
ADD updated TIMESTAMP;

ALTER TABLE electoral_district 
ALTER COLUMN updated 
SET DEFAULT CURRENT_TIMESTAMP;

UPDATE electoral_district 
SET updated=CURRENT_TIMESTAMP;

CREATE OR REPLACE FUNCTION update_updated_column()
RETURNS TRIGGER AS '
BEGIN
	NEW.updated = NOW();
	RETURN NEW;
		END;
		' LANGUAGE 'plpgsql';

		CREATE TRIGGER update_updated_modtime BEFORE UPDATE
		ON electoral_district FOR EACH ROW EXECUTE PROCEDURE
		update_updated_column();
