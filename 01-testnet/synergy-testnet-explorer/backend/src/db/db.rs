use sqlx::{PgPool, Error};

pub async fn init_db(pool: &PgPool) -> Result<(), Error> {
    sqlx::query!(
        "CREATE TABLE IF NOT EXISTS blocks (
            id SERIAL PRIMARY KEY,
            hash TEXT NOT NULL,
            previous_hash TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT NOW()
        )"
    )
    .execute(pool)
    .await?;

    Ok(())
}
