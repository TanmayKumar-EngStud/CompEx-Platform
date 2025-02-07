/*
  Warnings:

  - You are about to drop the column `mockquetionnumber` on the `problems` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE "problems" DROP COLUMN "mockquetionnumber",
ADD COLUMN     "mockquestionnumber" INTEGER;
