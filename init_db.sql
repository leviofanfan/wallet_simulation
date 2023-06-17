CREATE TABLE IF NOT EXISTS "users" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(60) NOT NULL,
    surname VARCHAR(60) NOT NULL,
    email VARCHAR(60) NOT NULL UNIQUE,
    created_at DATE DEFAULT CURRENT_DATE
    );


CREATE TABLE IF NOT EXISTS "wallets" (
    "id" SERIAL PRIMARY KEY,
    "number" VARCHAR(16) NOT NULL UNIQUE,
    "currency" VARCHAR(3) NOT NULL,
    "balance" FLOAT DEFAULT 0.0,
    "created_at" DATE DEFAULT CURRENT_DATE,
    "updated_at" DATE DEFAULT CURRENT_DATE,
    "is_active" BOOLEAN DEFAULT TRUE,
    "owner_id" INT,
    CONSTRAINT fk_owner
FOREIGN KEY (owner_id)
REFERENCES users(id)
ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS "TransferLog"(
    "transfer_uid" UUID PRIMARY KEY,
    "sender" VARCHAR(16) NOT NULL,
    "receiver" VARCHAR(16) NOT NULL,
    "currency_sent" VARCHAR(3) NOT NULL,
    "currency_received" VARCHAR(3) NOT NULL,
    "money_sent" FLOAT(2) NOT NULL,
    "money_received" FLOAT NOT NULL,
    "paid_on" TIMESTAMP DEFAULT now()
);
