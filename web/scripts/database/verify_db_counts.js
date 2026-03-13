
const { Client } = require('pg');

async function checkTables() {
    const client = new Client({
        connectionString: process.env.DATABASE_URL || "postgresql://compexe_admin:QuiZA.0310!@localhost:5433/compex-db"
    });

    await client.connect();

    const tables = [
        'users',
        'user_overall_performance',
        'user_tag_performance',
        'user_difficulty_stats',
        'mock_community_aggregates',
        'mock_score_distribution_stats',
        'mocktestrankings'
    ];

    for (const table of tables) {
        try {
            const res = await client.query(`SELECT COUNT(*) FROM ${table}`);
            console.log(`Table ${table}: ${res.rows[0].count} records`);
        } catch (e) {
            console.error(`Error checking ${table}:`, e.message);
        }
    }

    await client.end();
}

checkTables().catch(console.error);
