CREATE EVENT IF NOT EXISTS UpdateMetadataForNewTables
ON SCHEDULE EVERY 1 MINUTE
DO
BEGIN
    DECLARE finished INTEGER DEFAULT 0;
    DECLARE tableName VARCHAR(255); 
    DECLARE cur CURSOR FOR SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
                           WHERE TABLE_SCHEMA = 'swastik_test' AND TABLE_NAME != 'test_database_meta'; 
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET finished = 1;

    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO tableName;
        IF finished = 1 THEN 
            LEAVE read_loop;
        END IF;

        IF (SELECT COUNT(*) FROM test_database_meta WHERE table_name = tableName) > 0 THEN
            UPDATE test_database_meta
            SET column_name = (SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = tableName LIMIT 1),
                data_type = (SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = tableName LIMIT 1),
                data_length = (SELECT CHARACTER_MAXIMUM_LENGTH FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = tableName LIMIT 1),
                nullable = (SELECT IS_NULLABLE = 'YES' FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = tableName LIMIT 1),
                default_value = (SELECT COLUMN_DEFAULT FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = tableName LIMIT 1),
                is_primary_key = (SELECT COLUMN_KEY = 'PRI' FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = tableName LIMIT 1),
                is_unique = (SELECT COLUMN_KEY = 'UNI' FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = tableName LIMIT 1),
                updated_at = NOW()
            WHERE table_name = tableName;
        ELSE
            INSERT INTO test_database_meta (table_name, column_name, data_type, data_length, nullable, default_value, is_primary_key, is_unique, created_at)
            SELECT 
                TABLE_NAME, 
                COLUMN_NAME, 
                DATA_TYPE, 
                CHARACTER_MAXIMUM_LENGTH, 
                IS_NULLABLE = 'YES', 
                COLUMN_DEFAULT, 
                COLUMN_KEY = 'PRI', 
                COLUMN_KEY = 'UNI', 
                NOW()
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = tableName;
        END IF;

    END LOOP;

    CLOSE cur;
END;