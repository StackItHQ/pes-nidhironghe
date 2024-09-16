CREATE DATABASE Superjoin_Hiring_Process;

USE Superjoin_Hiring_Process;


CREATE TABLE candidates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id VARCHAR(10) UNIQUE NOT NULL,
    candidate_name VARCHAR(255) NOT NULL,
    interview_score INT NOT NULL,
    strength VARCHAR(255),
    weakness VARCHAR(255),
    feedback TEXT
);


INSERT INTO candidates (candidate_id, candidate_name, interview_score, strength, weakness, feedback)
VALUES
('CN1', 'Alan Algorithms', 90, 'Logical problem-solving', 'Over-explains concepts', 'Great at logic, but tends to overthink.'),
('CN2', 'Sarah Syntax', 94, 'Clean code and efficiency', 'Dislikes pseudocode', 'Efficient coder, allergic to pseudocode.'),
('CN3', 'Dave Debugger', 85, 'Strong debugging skills', 'Slow under pressure', 'A bug hunter, but slows down when stressed.'),
('CN4', 'Nina NeuralNet', 95, 'Machine learning wizardry', 'Overuses buzzwords', 'ML genius, but talks in too many acronyms.'),
('CN5', 'Lucy Loops', 95, 'Persistence in problem-solving', 'Prone to infinite loops', 'Never gives up, sometimes never stops either.'),
('CN6', 'Chris Cloud', 90, 'Cloud architecture expert', 'Prefers AWS to GCP', 'Cloud pro, but refuses to touch GCP.');


INSERT INTO candidates (candidate_id, candidate_name, interview_score, strength, weakness, feedback)
VALUES
('CN16', 'someone', 80, 'Logical problem-solving', 'does not explain concepts well', 'Great at logic, but tends to overthink.');

INSERT INTO candidates (candidate_id, candidate_name, interview_score, strength, weakness, feedback)
VALUES
('CN13', 'someone', 80, 'Logical problem-solving', 'does not explain concepts well', 'Great at logic, but tends to overthink.');

ALTER TABLE candidates
ADD COLUMN last_updated DATETIME;


select * from candidates;

DELETE FROM candidates WHERE id >= 5;


drop table candidates;