# Record Label DB Concurrency and GUI

# Overview
This project showcases a Java-based GUI for performing CRUD operations on a PostgreSQL database and a Python-based demonstration of concurrency issues in PostgreSQL and MySQL. The database models a record label, managing artists, albums, genres, and tracks.

# Features

**Java GUI (PostgreSQL)**
- User-friendly interface for managing Artists, Albums, Genres, and Tracks
- Full CRUD (Create, Read, Update, Delete) functionality
- PostgreSQL integration for real-time database operations

**Python Concurrency Issues (PostgreSQL & MySQL)**
- Simulates real-world concurrent transactions
- Demonstrates race conditions, deadlocks, and isolation levels
- Highlights differences between PostgreSQL and MySQL in handling concurrency

# Database Structure
The database consists of the following tables:
- **Artists**: Stores artist details
- **Albums**: Albums linked to artists
- **Genres**: Music genres
- **Tracks**: Individual tracks in an album
- **ArtistGenres**: Many-to-many relationship between artists and genres

```sql
CREATE DATABASE RecordLabel;
USE RecordLabel;

CREATE TABLE Artists (
    ArtistID INT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Country VARCHAR(255),
    Active TINYINT NOT NULL
);

CREATE TABLE Genres (
    GenreID INT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL
);

CREATE TABLE Albums (
    AlbumID INT PRIMARY KEY,
    Title VARCHAR(255) NOT NULL,
    ReleaseDate DATE,
    ArtistID INT,
    FOREIGN KEY (ArtistID) REFERENCES Artists(ArtistID) ON DELETE CASCADE
);

CREATE TABLE Tracks (
    TrackID INT PRIMARY KEY,
    Title VARCHAR(255) NOT NULL,
    AlbumID INT,
    FOREIGN KEY (AlbumID) REFERENCES Albums(AlbumID) ON DELETE CASCADE
);

CREATE TABLE ArtistGenres (
    ArtistID INT,
    GenreID INT,
    PRIMARY KEY (ArtistID, GenreID),
    FOREIGN KEY (ArtistID) REFERENCES Artists(ArtistID) ON DELETE CASCADE,
    FOREIGN KEY (GenreID) REFERENCES Genres(GenreID) ON DELETE CASCADE
);
```
