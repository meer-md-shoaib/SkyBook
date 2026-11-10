-- SkyBook database schema
-- MySQL / MariaDB 10.4+  (XAMPP defaults: root user, no password)
--
-- Usage:
--   mysql -u root < database/schema.sql
--   mysql -u root < database/seed.sql
--
-- Or simply run:  flask --app run.py reset-db

CREATE DATABASE IF NOT EXISTS skybook_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE skybook_db;

SET FOREIGN_KEY_CHECKS = 0;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `airports` (
  `airport_id` int(11) NOT NULL AUTO_INCREMENT,
  `airport_code` varchar(3) NOT NULL,
  `airport_name` varchar(120) NOT NULL,
  `city` varchar(80) NOT NULL,
  `country` varchar(80) NOT NULL,
  PRIMARY KEY (`airport_id`),
  UNIQUE KEY `ix_airports_airport_code` (`airport_code`),
  KEY `ix_airports_city` (`city`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `booking_seats` (
  `booking_seat_id` int(11) NOT NULL AUTO_INCREMENT,
  `booking_id` int(11) NOT NULL,
  `seat_id` int(11) NOT NULL,
  `active_seat_id` int(11) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`booking_seat_id`),
  UNIQUE KEY `uq_booking_seat` (`booking_id`,`seat_id`),
  UNIQUE KEY `uq_active_seat` (`active_seat_id`),
  KEY `ix_booking_seats_booking_id` (`booking_id`),
  KEY `ix_booking_seats_seat_id` (`seat_id`),
  CONSTRAINT `booking_seats_ibfk_1` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`booking_id`) ON DELETE CASCADE,
  CONSTRAINT `booking_seats_ibfk_2` FOREIGN KEY (`seat_id`) REFERENCES `seats` (`seat_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bookings` (
  `booking_id` int(11) NOT NULL AUTO_INCREMENT,
  `booking_reference` varchar(12) NOT NULL,
  `user_id` int(11) NOT NULL,
  `schedule_id` int(11) NOT NULL,
  `total_amount` decimal(10,2) NOT NULL,
  `booking_status` enum('PENDING','CONFIRMED','CANCELLED','EXPIRED') NOT NULL,
  `contact_email` varchar(120) DEFAULT NULL,
  `contact_phone` varchar(20) DEFAULT NULL,
  `hold_expires_at` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`booking_id`),
  UNIQUE KEY `ix_bookings_booking_reference` (`booking_reference`),
  KEY `ix_booking_user_status` (`user_id`,`booking_status`),
  KEY `ix_bookings_hold_expires_at` (`hold_expires_at`),
  KEY `ix_bookings_booking_status` (`booking_status`),
  KEY `ix_bookings_user_id` (`user_id`),
  KEY `ix_bookings_schedule_id` (`schedule_id`),
  CONSTRAINT `bookings_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `bookings_ibfk_2` FOREIGN KEY (`schedule_id`) REFERENCES `flight_schedules` (`schedule_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cancellations` (
  `cancellation_id` int(11) NOT NULL AUTO_INCREMENT,
  `booking_id` int(11) NOT NULL,
  `cancellation_reason` varchar(255) DEFAULT NULL,
  `refund_amount` decimal(10,2) NOT NULL,
  `cancellation_date` datetime NOT NULL,
  `refund_status` enum('PENDING','PROCESSED','REJECTED') NOT NULL,
  `processed_at` datetime DEFAULT NULL,
  PRIMARY KEY (`cancellation_id`),
  UNIQUE KEY `ix_cancellations_booking_id` (`booking_id`),
  KEY `ix_cancellations_refund_status` (`refund_status`),
  CONSTRAINT `cancellations_ibfk_1` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`booking_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `flight_schedules` (
  `schedule_id` int(11) NOT NULL AUTO_INCREMENT,
  `flight_id` int(11) NOT NULL,
  `departure_time` datetime NOT NULL,
  `arrival_time` datetime NOT NULL,
  `base_fare` decimal(10,2) NOT NULL,
  `status` enum('SCHEDULED','DEPARTED','CANCELLED','COMPLETED') NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`schedule_id`),
  KEY `ix_flight_schedules_flight_id` (`flight_id`),
  KEY `ix_flight_schedules_departure_time` (`departure_time`),
  KEY `ix_schedule_route_time` (`departure_time`),
  KEY `ix_flight_schedules_status` (`status`),
  CONSTRAINT `flight_schedules_ibfk_1` FOREIGN KEY (`flight_id`) REFERENCES `flights` (`flight_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=121 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `flights` (
  `flight_id` int(11) NOT NULL AUTO_INCREMENT,
  `flight_number` varchar(10) NOT NULL,
  `airline_name` varchar(80) NOT NULL,
  `source_airport_id` int(11) NOT NULL,
  `destination_airport_id` int(11) NOT NULL,
  `aircraft_type` varchar(40) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`flight_id`),
  UNIQUE KEY `ix_flights_flight_number` (`flight_number`),
  KEY `ix_flights_destination_airport_id` (`destination_airport_id`),
  KEY `ix_flights_source_airport_id` (`source_airport_id`),
  CONSTRAINT `flights_ibfk_1` FOREIGN KEY (`source_airport_id`) REFERENCES `airports` (`airport_id`),
  CONSTRAINT `flights_ibfk_2` FOREIGN KEY (`destination_airport_id`) REFERENCES `airports` (`airport_id`),
  CONSTRAINT `ck_flight_distinct_airports` CHECK (`source_airport_id` <> `destination_airport_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `passengers` (
  `passenger_id` int(11) NOT NULL AUTO_INCREMENT,
  `booking_id` int(11) NOT NULL,
  `full_name` varchar(120) NOT NULL,
  `date_of_birth` date NOT NULL,
  `gender` enum('MALE','FEMALE','OTHER') NOT NULL,
  `identification_type` varchar(30) NOT NULL,
  `identification_number` varchar(40) NOT NULL,
  `seat_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`passenger_id`),
  KEY `seat_id` (`seat_id`),
  KEY `ix_passengers_booking_id` (`booking_id`),
  CONSTRAINT `passengers_ibfk_1` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`booking_id`) ON DELETE CASCADE,
  CONSTRAINT `passengers_ibfk_2` FOREIGN KEY (`seat_id`) REFERENCES `seats` (`seat_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `payments` (
  `payment_id` int(11) NOT NULL AUTO_INCREMENT,
  `booking_id` int(11) NOT NULL,
  `transaction_reference` varchar(40) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `currency` varchar(3) NOT NULL,
  `payment_method` varchar(30) NOT NULL,
  `payment_status` enum('PENDING','SUCCESS','FAILED','REFUNDED') NOT NULL,
  `gateway_message` varchar(255) DEFAULT NULL,
  `attempts` int(11) NOT NULL,
  `payment_time` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`payment_id`),
  UNIQUE KEY `ix_payments_transaction_reference` (`transaction_reference`),
  UNIQUE KEY `ix_payments_booking_id` (`booking_id`),
  KEY `ix_payments_payment_status` (`payment_status`),
  CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`booking_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `seats` (
  `seat_id` int(11) NOT NULL AUTO_INCREMENT,
  `schedule_id` int(11) NOT NULL,
  `seat_number` varchar(5) NOT NULL,
  `seat_class` enum('ECONOMY','BUSINESS','FIRST') NOT NULL,
  `seat_row` int(11) NOT NULL,
  `seat_column` varchar(1) NOT NULL,
  `status` enum('AVAILABLE','HELD','BOOKED') NOT NULL,
  `current_booking_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`seat_id`),
  UNIQUE KEY `uq_seat_schedule_number` (`schedule_id`,`seat_number`),
  KEY `current_booking_id` (`current_booking_id`),
  KEY `ix_seats_schedule_id` (`schedule_id`),
  KEY `ix_seats_seat_class` (`seat_class`),
  KEY `ix_seats_status` (`status`),
  KEY `ix_seat_schedule_status` (`schedule_id`,`status`),
  CONSTRAINT `seats_ibfk_1` FOREIGN KEY (`schedule_id`) REFERENCES `flight_schedules` (`schedule_id`) ON DELETE CASCADE,
  CONSTRAINT `seats_ibfk_2` FOREIGN KEY (`current_booking_id`) REFERENCES `bookings` (`booking_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=15841 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tickets` (
  `ticket_id` int(11) NOT NULL AUTO_INCREMENT,
  `booking_id` int(11) NOT NULL,
  `ticket_number` varchar(20) NOT NULL,
  `generated_at` datetime NOT NULL,
  `file_path` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ticket_id`),
  UNIQUE KEY `ix_tickets_ticket_number` (`ticket_number`),
  UNIQUE KEY `ix_tickets_booking_id` (`booking_id`),
  CONSTRAINT `tickets_ibfk_1` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`booking_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(120) NOT NULL,
  `email` varchar(120) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `role` enum('PASSENGER','ADMIN') NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `ix_users_email` (`email`),
  KEY `ix_users_role` (`role`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;


SET FOREIGN_KEY_CHECKS = 1;
