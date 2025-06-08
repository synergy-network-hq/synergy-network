use sqlx::{Pool, Postgres};
use std::env;

/// Initializes and returns a database connection pool
#[allow(dead_code)]
pub async fn connect() -> Pool<Postgres> {
    let database_url = env::var("DATABASE_URL").expect("DATABASE_URL must be set");
    sqlx::PgPool::connect(&database_url)
        .await
        .expect("Failed to connect to database")
}
