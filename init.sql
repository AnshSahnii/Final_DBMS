
CREATE DATABASE IF NOT EXISTS bloodDonation;
USE bloodDonation; 
CREATE TABLE IF NOT EXISTS doctor (
         doctor_id INT NOT NULL AUTO_INCREMENT, 
         doctor_name VARCHAR(50), 
         doctor_phone BIGINT, 
         PRIMARY KEY(doctor_id) 
     ); 

CREATE TABLE IF NOT EXISTS donor (
         donor_id INT NOT NULL AUTO_INCREMENT, 
         donor_name VARCHAR(50), 
         phone_no BIGINT, 
         DOB DATE, 
         gender CHAR(1), 
         address VARCHAR(100), 
         weight INT, 
         blood_pressure INT, 
         iron_content INT, 
         doctor_id INT, 
         PRIMARY KEY(donor_id), 
         FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id) 
     ); 

CREATE TABLE IF NOT EXISTS blood_bank (
         blood_bank_id INT NOT NULL AUTO_INCREMENT, 
         blood_bank_name VARCHAR(50), 
         baddress VARCHAR(100), 
         PRIMARY KEY(blood_bank_id) 
     ); 

CREATE TABLE IF NOT EXISTS blood_stock (
         blood_type VARCHAR(20), 
         blood_bank_id INT, 
         units_available INT DEFAULT 0, 
         PRIMARY KEY (blood_type, blood_bank_id), 
         FOREIGN KEY (blood_bank_id) REFERENCES blood_bank(blood_bank_id) 
     ); 

CREATE TABLE IF NOT EXISTS users (
         id INT AUTO_INCREMENT PRIMARY KEY, 
         name VARCHAR(100) NOT NULL, 
         username VARCHAR(100) UNIQUE NOT NULL, 
         email VARCHAR(100) UNIQUE NOT NULL, 
         password VARCHAR(255) NOT NULL, 
         blood_group VARCHAR(5), 
         phone VARCHAR(20), 
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
     ); 

CREATE TABLE IF NOT EXISTS blood_request (
         request_id INT NOT NULL AUTO_INCREMENT, 
         blood_type VARCHAR(20), 
         units_requested INT, 
         doctor_id INT, 
         blood_bank_id INT, 
         user_id INT,  -- New column for user association 
         request_date DATE, 
         status VARCHAR(20) DEFAULT 'Pending', 
         PRIMARY KEY(request_id), 
         FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id), 
         FOREIGN KEY (blood_bank_id) REFERENCES blood_bank(blood_bank_id), 
         FOREIGN KEY (user_id) REFERENCES users(id)  -- Foreign Key to users table 
     ); 

CREATE TABLE IF NOT EXISTS blood_donations (
         donation_id INT NOT NULL AUTO_INCREMENT, 
         user_id INT, 
         blood_type VARCHAR(20), 
         units_donated INT, 
         blood_bank_id INT, 
         donation_date DATE, 
         PRIMARY KEY(donation_id), 
         FOREIGN KEY (user_id) REFERENCES users(id), 
         FOREIGN KEY (blood_bank_id) REFERENCES blood_bank(blood_bank_id) 
     ); 

DELIMITER //

CREATE TRIGGER update_last_donation
AFTER INSERT ON blood_donations
FOR EACH ROW
BEGIN
    UPDATE donor
    SET last_donation_date = CURRENT_DATE
    WHERE donor_id = NEW.user_id;
END //

DELIMITER ;

INSERT INTO blood_bank (blood_bank_name, baddress)
     VALUES 
     ('AIIMS Blood Bank', 'Ansari Nagar, New Delhi, Delhi'), 
     ('Bharati Vidyapeeth Blood Bank', 'Pune-Satara Rd, Pune, Maharashtra'), 
     ('KEM Hospital Blood Bank', 'Acharya Donde Marg, Parel, Mumbai, Maharashtra'), 
     ('Manipal Hospital Blood Bank', 'Manipal, Udupi, Karnataka'), 
     ('Apollo Hospitals Blood Bank', 'Banjara Hills, Hyderabad, Telangana'), 
     ('Fortis Blood Bank', 'Sector 62, Mohali, Punjab'), 
     ('Sankara Nethralaya Blood Bank', 'Mount Road, Chennai, Tamil Nadu'), 
     ('JIPMER Blood Bank', 'Dhanvantri Nagar, Puducherry'), 
     ('Rajiv Gandhi Cancer Institute Blood Bank', 'Sector-5, Rohini, Delhi'), 
     ('NIMHANS Blood Bank', 'Hosur Road, Bengaluru, Karnataka');