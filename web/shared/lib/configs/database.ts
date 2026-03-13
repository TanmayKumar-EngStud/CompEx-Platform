import { Pool } from "pg";

// initializing the pool with given Environment variables
const pool = new Pool({
   host: process.env.DATABASE_HOST as string,
   port: parseInt(process.env.DATABASE_PORT as string, 10),
   user: process.env.DATABASE_USER as string,
   password: process.env.DATABASE_PASSWORD as string,
   database: process.env.DATABASE_NAME as string,
});
// Function to run query using the pool.
export const query = (text: string, params?: any[]) => pool.query(text, params);