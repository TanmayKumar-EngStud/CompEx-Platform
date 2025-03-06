-- DropForeignKey
ALTER TABLE "mocksections" DROP CONSTRAINT "mocksections_mocktestid_fkey";

-- DropForeignKey
ALTER TABLE "mocksections" DROP CONSTRAINT "mocksections_sectionid_fkey";

-- DropForeignKey
ALTER TABLE "mocktestrankings" DROP CONSTRAINT "mocktestrankings_mocktestid_fkey";

-- DropForeignKey
ALTER TABLE "mocktestrankings" DROP CONSTRAINT "mocktestrankings_userid_fkey";

-- DropForeignKey
ALTER TABLE "mocktests" DROP CONSTRAINT "mocktests_examtypeid_fkey";

-- DropForeignKey
ALTER TABLE "mocktestsectionscores" DROP CONSTRAINT "mocktestsectionscores_attemptid_fkey";

-- DropForeignKey
ALTER TABLE "mocktestsectionscores" DROP CONSTRAINT "mocktestsectionscores_sectionid_fkey";

-- DropForeignKey
ALTER TABLE "performance" DROP CONSTRAINT "performance_sectionid_fkey";

-- DropForeignKey
ALTER TABLE "performance" DROP CONSTRAINT "performance_userid_fkey";

-- DropForeignKey
ALTER TABLE "problemoptions" DROP CONSTRAINT "problemoptions_problemid_fkey";

-- DropForeignKey
ALTER TABLE "problems" DROP CONSTRAINT "problems_examtypeid_fkey";

-- DropForeignKey
ALTER TABLE "problems" DROP CONSTRAINT "problems_mocksectionid_fkey";

-- DropForeignKey
ALTER TABLE "problems" DROP CONSTRAINT "problems_problemsSetId_fkey";

-- DropForeignKey
ALTER TABLE "problems" DROP CONSTRAINT "problems_sectionid_fkey";

-- DropForeignKey
ALTER TABLE "problemtags" DROP CONSTRAINT "problemtags_problemid_fkey";

-- DropForeignKey
ALTER TABLE "problemtags" DROP CONSTRAINT "problemtags_tagid_fkey";

-- DropForeignKey
ALTER TABLE "sections" DROP CONSTRAINT "sections_examtypeid_fkey";

-- DropForeignKey
ALTER TABLE "tags" DROP CONSTRAINT "tags_examtypeid_fkey";

-- DropForeignKey
ALTER TABLE "tags" DROP CONSTRAINT "tags_sectionid_fkey";

-- DropForeignKey
ALTER TABLE "userattempts" DROP CONSTRAINT "userattempts_problemid_fkey";

-- DropForeignKey
ALTER TABLE "userattempts" DROP CONSTRAINT "userattempts_userid_fkey";

-- DropForeignKey
ALTER TABLE "usermocktestattempts" DROP CONSTRAINT "usermocktestattempts_mocktestid_fkey";

-- DropForeignKey
ALTER TABLE "usermocktestattempts" DROP CONSTRAINT "usermocktestattempts_userid_fkey";

-- DropForeignKey
ALTER TABLE "userstreaks" DROP CONSTRAINT "userstreaks_userid_fkey";

-- AddForeignKey
ALTER TABLE "mocktestrankings" ADD CONSTRAINT "mocktestrankings_mocktestid_fkey" FOREIGN KEY ("mocktestid") REFERENCES "mocktests"("mocktestid") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "mocktestrankings" ADD CONSTRAINT "mocktestrankings_userid_fkey" FOREIGN KEY ("userid") REFERENCES "users"("userid") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "mocktests" ADD CONSTRAINT "mocktests_examtypeid_fkey" FOREIGN KEY ("examtypeid") REFERENCES "examtypes"("examtypeid") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "mocktestsectionscores" ADD CONSTRAINT "mocktestsectionscores_attemptid_fkey" FOREIGN KEY ("attemptid") REFERENCES "usermocktestattempts"("attemptid") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "mocktestsectionscores" ADD CONSTRAINT "mocktestsectionscores_sectionid_fkey" FOREIGN KEY ("sectionid") REFERENCES "sections"("sectionid") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "mocksections" ADD CONSTRAINT "mocksections_mocktestid_fkey" FOREIGN KEY ("mocktestid") REFERENCES "mocktests"("mocktestid") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "mocksections" ADD CONSTRAINT "mocksections_sectionid_fkey" FOREIGN KEY ("sectionid") REFERENCES "sections"("sectionid") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "performance" ADD CONSTRAINT "performance_sectionid_fkey" FOREIGN KEY ("sectionid") REFERENCES "sections"("sectionid") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "performance" ADD CONSTRAINT "performance_userid_fkey" FOREIGN KEY ("userid") REFERENCES "users"("userid") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "problemoptions" ADD CONSTRAINT "problemoptions_problemid_fkey" FOREIGN KEY ("problemid") REFERENCES "problems"("problemid") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "problems" ADD CONSTRAINT "problems_examtypeid_fkey" FOREIGN KEY ("examtypeid") REFERENCES "examtypes"("examtypeid") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "problems" ADD CONSTRAINT "problems_mocksectionid_fkey" FOREIGN KEY ("mocksectionid") REFERENCES "mocksections"("mocksectionid") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "problems" ADD CONSTRAINT "problems_problemsSetId_fkey" FOREIGN KEY ("problemsSetId") REFERENCES "ProblemsSet"("problemsSetId") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "problems" ADD CONSTRAINT "problems_sectionid_fkey" FOREIGN KEY ("sectionid") REFERENCES "sections"("sectionid") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "problemtags" ADD CONSTRAINT "problemtags_problemid_fkey" FOREIGN KEY ("problemid") REFERENCES "problems"("problemid") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "problemtags" ADD CONSTRAINT "problemtags_tagid_fkey" FOREIGN KEY ("tagid") REFERENCES "tags"("tagid") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "sections" ADD CONSTRAINT "sections_examtypeid_fkey" FOREIGN KEY ("examtypeid") REFERENCES "examtypes"("examtypeid") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "tags" ADD CONSTRAINT "tags_examtypeid_fkey" FOREIGN KEY ("examtypeid") REFERENCES "examtypes"("examtypeid") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "tags" ADD CONSTRAINT "tags_sectionid_fkey" FOREIGN KEY ("sectionid") REFERENCES "sections"("sectionid") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "userattempts" ADD CONSTRAINT "userattempts_problemid_fkey" FOREIGN KEY ("problemid") REFERENCES "problems"("problemid") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "userattempts" ADD CONSTRAINT "userattempts_userid_fkey" FOREIGN KEY ("userid") REFERENCES "users"("userid") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "usermocktestattempts" ADD CONSTRAINT "usermocktestattempts_mocktestid_fkey" FOREIGN KEY ("mocktestid") REFERENCES "mocktests"("mocktestid") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "usermocktestattempts" ADD CONSTRAINT "usermocktestattempts_userid_fkey" FOREIGN KEY ("userid") REFERENCES "users"("userid") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "userstreaks" ADD CONSTRAINT "userstreaks_userid_fkey" FOREIGN KEY ("userid") REFERENCES "users"("userid") ON DELETE CASCADE ON UPDATE CASCADE;
