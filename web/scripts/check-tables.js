
const { Client } = require('pg');

const client = new Client({
    connectionString: 'postgresql://compexe_admin:QuiZA.0310!@127.0.0.1:5433/artilaries',
});

async function listTables() {
    try {
        console.log("Connecting to artilaries DB...");
        await client.connect();

        const res = await client.query(`
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        `);

        if (res.rows.length === 0) {
            console.log("No tables found! Database is empty.");
        } else {
            console.log("Tables found:", res.rows.map(r => r.table_name).join(', '));

            // Check for examtypes data specifically
            try {
                const exams = await client.query('SELECT * FROM "examtypes"');
                console.log(`ExamTypes count: ${exams.rows.length}`);
                if (exams.rows.length > 0) {
                    console.log("Exams:", exams.rows.map(e => e.name).join(', '));
                }
            } catch (e) {
                console.log("Could not query examtypes table.");
            }
        }

        await client.end();
    } catch (err) {
        console.error("Error:", err);
    }
}

listTables();
