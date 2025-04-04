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
