
const { Client } = require('pg');

// Connect to the 'postgres' default database to list others
const client = new Client({
    connectionString: 'postgresql://compexe_admin:QuiZA.0310!@127.0.0.1:5433/postgres',
});

async function listDatabases() {
    try {
        console.log("Connecting to Postgres system DB...");
        await client.connect();
        console.log("Connected! Listing databases:");

        const res = await client.query('SELECT datname FROM pg_database WHERE datistemplate = false;');
        res.rows.forEach(row => {
            console.log(` - ${row.datname}`);
        });

        await client.end();
    } catch (err) {
        console.error("Listing error:", err);
    }
}

listDatabases();
