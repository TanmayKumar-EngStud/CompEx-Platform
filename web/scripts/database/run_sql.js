
const { Client } = require('pg');
const fs = require('fs');
const path = require('path');

async function runSqlFile(filePath) {
    const client = new Client({
        connectionString: process.env.DATABASE_URL || "postgresql://compexe_admin:QuiZA.0310!@localhost:5433/compex-db"
    });

    try {
        await client.connect();
        console.log(`Connected to database for script: ${path.basename(filePath)}`);

        const sql = fs.readFileSync(filePath, 'utf8');
        await client.query(sql);

        console.log(`Successfully executed: ${path.basename(filePath)}`);
    } catch (err) {
        console.error(`Error executing ${path.basename(filePath)}:`, err.message);
        process.exit(1);
    } finally {
        await client.end();
    }
}

const action = process.argv[2];

if (action === 'setup') {
    runSqlFile(path.join(__dirname, 'setup_analytics_tables.sql'));
} else if (action === 'migrate') {
    runSqlFile(path.join(__dirname, 'migrate_analytics_data.sql'));
} else {
    console.log('Usage: node run_sql.js [setup|migrate]');
}
