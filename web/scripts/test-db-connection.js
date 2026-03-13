
const { Client } = require('pg');

const client = new Client({
    connectionString: 'postgresql://compexe_admin:QuiZA.0310!@127.0.0.1:5433/artilaries',
});

async function testConnection() {
    try {
        console.log("Connecting to DB...");
        await client.connect();
        console.log("Connected successfully!");
        const res = await client.query('SELECT NOW()');
        console.log("Database Time:", res.rows[0]);
        await client.end();
    } catch (err) {
        console.error("Connection error:", err);
    }
}

testConnection();
