-- CreateTable
CREATE TABLE "ProblemsSet" (
    "problemsSetId" SERIAL NOT NULL,
    "sectionid" INTEGER NOT NULL,
    "examtypeid" INTEGER NOT NULL,
    "title" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "content" JSONB NOT NULL,
    "mocksectionid" INTEGER,
    "mockquestionnumber" INTEGER,

    CONSTRAINT "ProblemsSet_pkey" PRIMARY KEY ("problemsSetId")
);

-- CreateTable
CREATE TABLE "examtypes" (
    "examtypeid" SERIAL NOT NULL,
    "name" VARCHAR(100) NOT NULL,
    "description" TEXT,

    CONSTRAINT "examtypes_pkey" PRIMARY KEY ("examtypeid")
);

-- CreateTable
CREATE TABLE "mocktestrankings" (
    "rankingid" SERIAL NOT NULL,
    "userid" INTEGER,
    "mocktestid" INTEGER,
    "rank" INTEGER,
    "percentile" DECIMAL(5,2),

    CONSTRAINT "mocktestrankings_pkey" PRIMARY KEY ("rankingid")
);

-- CreateTable
CREATE TABLE "mocktests" (
    "mocktestid" SERIAL NOT NULL,
    "difficulty" INTEGER NOT NULL DEFAULT 0,
    "examtypeid" INTEGER,
    "date" DATE NOT NULL,
    "starttime" TIME(6) NOT NULL,
    "endtime" TIME(6) NOT NULL,
    "isactive" BOOLEAN DEFAULT true,

    CONSTRAINT "mocktests_pkey" PRIMARY KEY ("mocktestid")
);

-- CreateTable
CREATE TABLE "mocktestsectionscores" (
    "scoreid" SERIAL NOT NULL,
    "attemptid" INTEGER,
    "sectionid" INTEGER,
    "score" DECIMAL(5,2),

    CONSTRAINT "mocktestsectionscores_pkey" PRIMARY KEY ("scoreid")
);

-- CreateTable
CREATE TABLE "mocksections" (
    "mocksectionid" SERIAL NOT NULL,
    "mocktestid" INTEGER NOT NULL,
    "sectionnumber" INTEGER NOT NULL,
    "sectionid" INTEGER NOT NULL,

    CONSTRAINT "mocksections_pkey" PRIMARY KEY ("mocksectionid")
);

-- CreateTable
CREATE TABLE "performance" (
    "userid" INTEGER NOT NULL,
    "sectionid" INTEGER NOT NULL,
    "correctcount" INTEGER DEFAULT 0,
    "incorrectcount" INTEGER DEFAULT 0,
    "partialcorrectcount" INTEGER DEFAULT 0,
    "averagespeed" interval,

    CONSTRAINT "performance_pkey" PRIMARY KEY ("userid","sectionid")
);

-- CreateTable
CREATE TABLE "problemoptions" (
    "optionid" SERIAL NOT NULL,
    "problemid" INTEGER,
    "optiontext" TEXT NOT NULL,
    "iscorrect" BOOLEAN,
    "group" TEXT,

    CONSTRAINT "problemoptions_pkey" PRIMARY KEY ("optionid")
);

-- CreateTable
CREATE TABLE "problems" (
    "type" TEXT,
    "prompt" TEXT,
    "problemid" SERIAL NOT NULL,
    "sectionid" INTEGER,
    "examtypeid" INTEGER,
    "title" VARCHAR(200) NOT NULL,
    "text" TEXT NOT NULL,
    "difficulty" INTEGER,
    "correctattemptscount" INTEGER DEFAULT 0,
    "totalattemptscount" INTEGER DEFAULT 0,
    "metadata" JSONB,
    "creationdate" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
    "addedDate" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
    "isChildren" BOOLEAN NOT NULL DEFAULT false,
    "problemsSetId" INTEGER,
    "mocksectionid" INTEGER,
    "mockquetionnumber" INTEGER,
    "isMockQuestion" BOOLEAN NOT NULL DEFAULT false,
    "solution" JSONB,

    CONSTRAINT "problems_pkey" PRIMARY KEY ("problemid")
);

-- CreateTable
CREATE TABLE "problemssettags" (
    "problemsSetId" INTEGER NOT NULL,
    "tagid" INTEGER NOT NULL,

    CONSTRAINT "problemssettags_pkey" PRIMARY KEY ("tagid","problemsSetId")
);

-- CreateTable
CREATE TABLE "problemtags" (
    "problemid" INTEGER NOT NULL,
    "tagid" INTEGER NOT NULL,

    CONSTRAINT "problemtags_pkey" PRIMARY KEY ("problemid","tagid")
);

-- CreateTable
CREATE TABLE "sections" (
    "sectionid" SERIAL NOT NULL,
    "examtypeid" INTEGER,
    "name" VARCHAR(100) NOT NULL,
    "description" TEXT,

    CONSTRAINT "sections_pkey" PRIMARY KEY ("sectionid")
);

-- CreateTable
CREATE TABLE "tags" (
    "tagid" SERIAL NOT NULL,
    "name" VARCHAR(50) NOT NULL,
    "examtypeid" INTEGER NOT NULL,
    "sectionid" INTEGER NOT NULL,

    CONSTRAINT "tags_pkey" PRIMARY KEY ("tagid")
);

-- CreateTable
CREATE TABLE "userattempt_selectedoptions" (
    "id" SERIAL NOT NULL,
    "userattemptid" INTEGER NOT NULL,
    "optionid" INTEGER NOT NULL,

    CONSTRAINT "userattempt_selectedoptions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "userattempts" (
    "attemptid" SERIAL NOT NULL,
    "userid" INTEGER,
    "problemid" INTEGER,
    "timetaken" TEXT,
    "attemptdate" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
    "partialcorrectnessscore" DECIMAL(5,2),
    "iscorrect" BOOLEAN,

    CONSTRAINT "userattempts_pkey" PRIMARY KEY ("attemptid")
);

-- CreateTable
CREATE TABLE "usermocktestattempts" (
    "attemptid" SERIAL NOT NULL,
    "userid" INTEGER,
    "mocktestid" INTEGER,
    "starttime" TIMESTAMP(6) NOT NULL,
    "endtime" TIMESTAMP(6),
    "totalscore" DECIMAL(5,2),
    "isofficialattempt" BOOLEAN DEFAULT true,

    CONSTRAINT "usermocktestattempts_pkey" PRIMARY KEY ("attemptid")
);

-- CreateTable
CREATE TABLE "users" (
    "userid" SERIAL NOT NULL,
    "username" VARCHAR(50) NOT NULL,
    "password" VARCHAR(100) NOT NULL,
    "email" VARCHAR(100) NOT NULL,
    "registrationdate" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "users_pkey" PRIMARY KEY ("userid")
);

-- CreateTable
CREATE TABLE "userstreaks" (
    "streakid" SERIAL NOT NULL,
    "userid" INTEGER,
    "currentstreak" INTEGER DEFAULT 0,
    "lasttestdate" DATE,
    "higheststreak" INTEGER DEFAULT 0,

    CONSTRAINT "userstreaks_pkey" PRIMARY KEY ("streakid")
);

-- CreateIndex
CREATE UNIQUE INDEX "userattempt_selectedoptions_userattemptid_optionid_key" ON "userattempt_selectedoptions"("userattemptid", "optionid");

-- CreateIndex
CREATE UNIQUE INDEX "users_username_key" ON "users"("username");

-- CreateIndex
CREATE UNIQUE INDEX "users_email_key" ON "users"("email");

-- AddForeignKey
ALTER TABLE "ProblemsSet" ADD CONSTRAINT "ProblemsSet_examtypeid_fkey" FOREIGN KEY ("examtypeid") REFERENCES "examtypes"("examtypeid") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ProblemsSet" ADD CONSTRAINT "ProblemsSet_mocksectionid_fkey" FOREIGN KEY ("mocksectionid") REFERENCES "mocksections"("mocksectionid") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ProblemsSet" ADD CONSTRAINT "ProblemsSet_sectionid_fkey" FOREIGN KEY ("sectionid") REFERENCES "sections"("sectionid") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "mocktestrankings" ADD CONSTRAINT "mocktestrankings_mocktestid_fkey" FOREIGN KEY ("mocktestid") REFERENCES "mocktests"("mocktestid") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "mocktestrankings" ADD CONSTRAINT "mocktestrankings_userid_fkey" FOREIGN KEY ("userid") REFERENCES "users"("userid") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "mocktests" ADD CONSTRAINT "mocktests_examtypeid_fkey" FOREIGN KEY ("examtypeid") REFERENCES "examtypes"("examtypeid") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "mocktestsectionscores" ADD CONSTRAINT "mocktestsectionscores_attemptid_fkey" FOREIGN KEY ("attemptid") REFERENCES "usermocktestattempts"("attemptid") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "mocktestsectionscores" ADD CONSTRAINT "mocktestsectionscores_sectionid_fkey" FOREIGN KEY ("sectionid") REFERENCES "sections"("sectionid") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "mocksections" ADD CONSTRAINT "mocksections_mocktestid_fkey" FOREIGN KEY ("mocktestid") REFERENCES "mocktests"("mocktestid") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "mocksections" ADD CONSTRAINT "mocksections_sectionid_fkey" FOREIGN KEY ("sectionid") REFERENCES "sections"("sectionid") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "performance" ADD CONSTRAINT "performance_sectionid_fkey" FOREIGN KEY ("sectionid") REFERENCES "sections"("sectionid") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "performance" ADD CONSTRAINT "performance_userid_fkey" FOREIGN KEY ("userid") REFERENCES "users"("userid") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "problemoptions" ADD CONSTRAINT "problemoptions_problemid_fkey" FOREIGN KEY ("problemid") REFERENCES "problems"("problemid") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "problems" ADD CONSTRAINT "problems_examtypeid_fkey" FOREIGN KEY ("examtypeid") REFERENCES "examtypes"("examtypeid") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "problems" ADD CONSTRAINT "problems_problemsSetId_fkey" FOREIGN KEY ("problemsSetId") REFERENCES "ProblemsSet"("problemsSetId") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "problems" ADD CONSTRAINT "problems_sectionid_fkey" FOREIGN KEY ("sectionid") REFERENCES "sections"("sectionid") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "problems" ADD CONSTRAINT "problems_mocksectionid_fkey" FOREIGN KEY ("mocksectionid") REFERENCES "mocksections"("mocksectionid") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "problemssettags" ADD CONSTRAINT "problemssettags_problemsSetId_fkey" FOREIGN KEY ("problemsSetId") REFERENCES "ProblemsSet"("problemsSetId") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "problemssettags" ADD CONSTRAINT "problemssettags_tagid_fkey" FOREIGN KEY ("tagid") REFERENCES "tags"("tagid") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "problemtags" ADD CONSTRAINT "problemtags_problemid_fkey" FOREIGN KEY ("problemid") REFERENCES "problems"("problemid") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "problemtags" ADD CONSTRAINT "problemtags_tagid_fkey" FOREIGN KEY ("tagid") REFERENCES "tags"("tagid") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "sections" ADD CONSTRAINT "sections_examtypeid_fkey" FOREIGN KEY ("examtypeid") REFERENCES "examtypes"("examtypeid") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "tags" ADD CONSTRAINT "tags_examtypeid_fkey" FOREIGN KEY ("examtypeid") REFERENCES "examtypes"("examtypeid") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "tags" ADD CONSTRAINT "tags_sectionid_fkey" FOREIGN KEY ("sectionid") REFERENCES "sections"("sectionid") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "userattempt_selectedoptions" ADD CONSTRAINT "userattempt_selectedoptions_optionid_fkey" FOREIGN KEY ("optionid") REFERENCES "problemoptions"("optionid") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "userattempt_selectedoptions" ADD CONSTRAINT "userattempt_selectedoptions_userattemptid_fkey" FOREIGN KEY ("userattemptid") REFERENCES "userattempts"("attemptid") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "userattempts" ADD CONSTRAINT "userattempts_problemid_fkey" FOREIGN KEY ("problemid") REFERENCES "problems"("problemid") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "userattempts" ADD CONSTRAINT "userattempts_userid_fkey" FOREIGN KEY ("userid") REFERENCES "users"("userid") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "usermocktestattempts" ADD CONSTRAINT "usermocktestattempts_mocktestid_fkey" FOREIGN KEY ("mocktestid") REFERENCES "mocktests"("mocktestid") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "usermocktestattempts" ADD CONSTRAINT "usermocktestattempts_userid_fkey" FOREIGN KEY ("userid") REFERENCES "users"("userid") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "userstreaks" ADD CONSTRAINT "userstreaks_userid_fkey" FOREIGN KEY ("userid") REFERENCES "users"("userid") ON DELETE NO ACTION ON UPDATE NO ACTION;
