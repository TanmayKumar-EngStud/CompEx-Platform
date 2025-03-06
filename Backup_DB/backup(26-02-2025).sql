--
-- PostgreSQL database dump
--

-- Dumped from database version 16.3 (Debian 16.3-1.pgdg120+1)
-- Dumped by pg_dump version 16.3 (Debian 16.3-1.pgdg120+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: compexe_admin
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO compexe_admin;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: compexe_admin
--

COMMENT ON SCHEMA public IS '';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: ProblemsSet; Type: TABLE; Schema: public; Owner: compexe_admin
--

CREATE TABLE public."ProblemsSet" (
    "problemsSetId" integer NOT NULL,
    sectionid integer NOT NULL,
    examtypeid integer NOT NULL,
    title text NOT NULL,
    type text NOT NULL,
    content jsonb NOT NULL,
    mocksectionid integer,
    mockquestionnumber integer
);


ALTER TABLE public."ProblemsSet" OWNER TO compexe_admin;

--
-- Name: ProblemsSet_problemsSetId_seq; Type: SEQUENCE; Schema: public; Owner: compexe_admin
--

CREATE SEQUENCE public."ProblemsSet_problemsSetId_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."ProblemsSet_problemsSetId_seq" OWNER TO compexe_admin;

--
-- Name: ProblemsSet_problemsSetId_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: compexe_admin
--

ALTER SEQUENCE public."ProblemsSet_problemsSetId_seq" OWNED BY public."ProblemsSet"."problemsSetId";


--
-- Name: _prisma_migrations; Type: TABLE; Schema: public; Owner: compexe_admin
--

CREATE TABLE public._prisma_migrations (
    id character varying(36) NOT NULL,
    checksum character varying(64) NOT NULL,
    finished_at timestamp with time zone,
    migration_name character varying(255) NOT NULL,
    logs text,
    rolled_back_at timestamp with time zone,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    applied_steps_count integer DEFAULT 0 NOT NULL
);


ALTER TABLE public._prisma_migrations OWNER TO compexe_admin;

--
-- Name: examtypes; Type: TABLE; Schema: public; Owner: compexe_admin
--

CREATE TABLE public.examtypes (
    examtypeid integer NOT NULL,
    name character varying(100) NOT NULL,
    description text
);


ALTER TABLE public.examtypes OWNER TO compexe_admin;

--
-- Name: examtypes_examtypeid_seq; Type: SEQUENCE; Schema: public; Owner: compexe_admin
--

CREATE SEQUENCE public.examtypes_examtypeid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.examtypes_examtypeid_seq OWNER TO compexe_admin;

--
-- Name: examtypes_examtypeid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: compexe_admin
--

ALTER SEQUENCE public.examtypes_examtypeid_seq OWNED BY public.examtypes.examtypeid;


--
-- Name: mocksections; Type: TABLE; Schema: public; Owner: compexe_admin
--

CREATE TABLE public.mocksections (
    mocksectionid integer NOT NULL,
    mocktestid integer NOT NULL,
    sectionnumber integer NOT NULL,
    sectionid integer NOT NULL
);


ALTER TABLE public.mocksections OWNER TO compexe_admin;

--
-- Name: mocksections_mocksectionid_seq; Type: SEQUENCE; Schema: public; Owner: compexe_admin
--

CREATE SEQUENCE public.mocksections_mocksectionid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mocksections_mocksectionid_seq OWNER TO compexe_admin;

--
-- Name: mocksections_mocksectionid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: compexe_admin
--

ALTER SEQUENCE public.mocksections_mocksectionid_seq OWNED BY public.mocksections.mocksectionid;


--
-- Name: mocktestrankings; Type: TABLE; Schema: public; Owner: compexe_admin
--

CREATE TABLE public.mocktestrankings (
    rankingid integer NOT NULL,
    userid integer,
    mocktestid integer,
    rank integer,
    percentile numeric(5,2)
);


ALTER TABLE public.mocktestrankings OWNER TO compexe_admin;

--
-- Name: mocktestrankings_rankingid_seq; Type: SEQUENCE; Schema: public; Owner: compexe_admin
--

CREATE SEQUENCE public.mocktestrankings_rankingid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mocktestrankings_rankingid_seq OWNER TO compexe_admin;

--
-- Name: mocktestrankings_rankingid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: compexe_admin
--

ALTER SEQUENCE public.mocktestrankings_rankingid_seq OWNED BY public.mocktestrankings.rankingid;


--
-- Name: mocktests; Type: TABLE; Schema: public; Owner: compexe_admin
--

CREATE TABLE public.mocktests (
    mocktestid integer NOT NULL,
    difficulty integer DEFAULT 0 NOT NULL,
    examtypeid integer,
    date date NOT NULL,
    starttime time(6) without time zone NOT NULL,
    endtime time(6) without time zone NOT NULL,
    isactive boolean DEFAULT true
);


ALTER TABLE public.mocktests OWNER TO compexe_admin;

--
-- Name: mocktests_mocktestid_seq; Type: SEQUENCE; Schema: public; Owner: compexe_admin
--

CREATE SEQUENCE public.mocktests_mocktestid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mocktests_mocktestid_seq OWNER TO compexe_admin;

--
-- Name: mocktests_mocktestid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: compexe_admin
--

ALTER SEQUENCE public.mocktests_mocktestid_seq OWNED BY public.mocktests.mocktestid;


--
-- Name: mocktestsectionscores; Type: TABLE; Schema: public; Owner: compexe_admin
--

CREATE TABLE public.mocktestsectionscores (
    scoreid integer NOT NULL,
    attemptid integer,
    sectionid integer,
    score numeric(5,2)
);


ALTER TABLE public.mocktestsectionscores OWNER TO compexe_admin;

--
-- Name: mocktestsectionscores_scoreid_seq; Type: SEQUENCE; Schema: public; Owner: compexe_admin
--

CREATE SEQUENCE public.mocktestsectionscores_scoreid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mocktestsectionscores_scoreid_seq OWNER TO compexe_admin;

--
-- Name: mocktestsectionscores_scoreid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: compexe_admin
--

ALTER SEQUENCE public.mocktestsectionscores_scoreid_seq OWNED BY public.mocktestsectionscores.scoreid;


--
-- Name: performance; Type: TABLE; Schema: public; Owner: compexe_admin
--

CREATE TABLE public.performance (
    userid integer NOT NULL,
    sectionid integer NOT NULL,
    correctcount integer DEFAULT 0,
    incorrectcount integer DEFAULT 0,
    partialcorrectcount integer DEFAULT 0,
    averagespeed interval
);


ALTER TABLE public.performance OWNER TO compexe_admin;

--
-- Name: problemoptions; Type: TABLE; Schema: public; Owner: compexe_admin
--

CREATE TABLE public.problemoptions (
    optionid integer NOT NULL,
    problemid integer,
    optiontext text NOT NULL,
    iscorrect boolean,
    "group" text
);


ALTER TABLE public.problemoptions OWNER TO compexe_admin;

--
-- Name: problemoptions_optionid_seq; Type: SEQUENCE; Schema: public; Owner: compexe_admin
--

CREATE SEQUENCE public.problemoptions_optionid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.problemoptions_optionid_seq OWNER TO compexe_admin;

--
-- Name: problemoptions_optionid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: compexe_admin
--

ALTER SEQUENCE public.problemoptions_optionid_seq OWNED BY public.problemoptions.optionid;


--
-- Name: problems; Type: TABLE; Schema: public; Owner: compexe_admin
--

CREATE TABLE public.problems (
    type text,
    prompt text,
    problemid integer NOT NULL,
    sectionid integer,
    examtypeid integer,
    title character varying(200) NOT NULL,
    text text NOT NULL,
    difficulty integer,
    correctattemptscount integer DEFAULT 0,
    totalattemptscount integer DEFAULT 0,
    metadata jsonb,
    creationdate timestamp(6) without time zone DEFAULT CURRENT_TIMESTAMP,
    "addedDate" timestamp(6) without time zone DEFAULT CURRENT_TIMESTAMP,
    "isChildren" boolean DEFAULT false NOT NULL,
    "problemsSetId" integer,
    mocksectionid integer,
    "isMockQuestion" boolean DEFAULT false NOT NULL,
    solution jsonb,
    mockquestionnumber integer
);


ALTER TABLE public.problems OWNER TO compexe_admin;

--
-- Name: problems_problemid_seq; Type: SEQUENCE; Schema: public; Owner: compexe_admin
--

CREATE SEQUENCE public.problems_problemid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.problems_problemid_seq OWNER TO compexe_admin;

--
-- Name: problems_problemid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: compexe_admin
--

ALTER SEQUENCE public.problems_problemid_seq OWNED BY public.problems.problemid;


--
-- Name: problemssettags; Type: TABLE; Schema: public; Owner: compexe_admin
--

CREATE TABLE public.problemssettags (
    "problemsSetId" integer NOT NULL,
    tagid integer NOT NULL
);


ALTER TABLE public.problemssettags OWNER TO compexe_admin;

--
-- Name: problemtags; Type: TABLE; Schema: public; Owner: compexe_admin
--

CREATE TABLE public.problemtags (
    problemid integer NOT NULL,
    tagid integer NOT NULL
);


ALTER TABLE public.problemtags OWNER TO compexe_admin;

--
-- Name: sections; Type: TABLE; Schema: public; Owner: compexe_admin
--

CREATE TABLE public.sections (
    sectionid integer NOT NULL,
    examtypeid integer,
    name character varying(100) NOT NULL,
    description text
);


ALTER TABLE public.sections OWNER TO compexe_admin;

--
-- Name: sections_sectionid_seq; Type: SEQUENCE; Schema: public; Owner: compexe_admin
--

CREATE SEQUENCE public.sections_sectionid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sections_sectionid_seq OWNER TO compexe_admin;

--
-- Name: sections_sectionid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: compexe_admin
--

ALTER SEQUENCE public.sections_sectionid_seq OWNED BY public.sections.sectionid;


--
-- Name: tags; Type: TABLE; Schema: public; Owner: compexe_admin
--

CREATE TABLE public.tags (
    tagid integer NOT NULL,
    name character varying(50) NOT NULL,
    examtypeid integer NOT NULL,
    sectionid integer NOT NULL
);


ALTER TABLE public.tags OWNER TO compexe_admin;

--
-- Name: tags_tagid_seq; Type: SEQUENCE; Schema: public; Owner: compexe_admin
--

CREATE SEQUENCE public.tags_tagid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tags_tagid_seq OWNER TO compexe_admin;

--
-- Name: tags_tagid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: compexe_admin
--

ALTER SEQUENCE public.tags_tagid_seq OWNED BY public.tags.tagid;


--
-- Name: userattempt_selectedoptions; Type: TABLE; Schema: public; Owner: compexe_admin
--

CREATE TABLE public.userattempt_selectedoptions (
    id integer NOT NULL,
    userattemptid integer NOT NULL,
    optionid integer NOT NULL
);


ALTER TABLE public.userattempt_selectedoptions OWNER TO compexe_admin;

--
-- Name: userattempt_selectedoptions_id_seq; Type: SEQUENCE; Schema: public; Owner: compexe_admin
--

CREATE SEQUENCE public.userattempt_selectedoptions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.userattempt_selectedoptions_id_seq OWNER TO compexe_admin;

--
-- Name: userattempt_selectedoptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: compexe_admin
--

ALTER SEQUENCE public.userattempt_selectedoptions_id_seq OWNED BY public.userattempt_selectedoptions.id;


--
-- Name: userattempts; Type: TABLE; Schema: public; Owner: compexe_admin
--

CREATE TABLE public.userattempts (
    attemptid integer NOT NULL,
    userid integer,
    problemid integer,
    timetaken text,
    attemptdate timestamp(6) without time zone DEFAULT CURRENT_TIMESTAMP,
    partialcorrectnessscore numeric(5,2),
    iscorrect boolean
);


ALTER TABLE public.userattempts OWNER TO compexe_admin;

--
-- Name: userattempts_attemptid_seq; Type: SEQUENCE; Schema: public; Owner: compexe_admin
--

CREATE SEQUENCE public.userattempts_attemptid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.userattempts_attemptid_seq OWNER TO compexe_admin;

--
-- Name: userattempts_attemptid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: compexe_admin
--

ALTER SEQUENCE public.userattempts_attemptid_seq OWNED BY public.userattempts.attemptid;


--
-- Name: usermocktestattempts; Type: TABLE; Schema: public; Owner: compexe_admin
--

CREATE TABLE public.usermocktestattempts (
    attemptid integer NOT NULL,
    userid integer,
    mocktestid integer,
    starttime timestamp(6) without time zone NOT NULL,
    endtime timestamp(6) without time zone,
    totalscore numeric(5,2),
    isofficialattempt boolean DEFAULT true
);


ALTER TABLE public.usermocktestattempts OWNER TO compexe_admin;

--
-- Name: usermocktestattempts_attemptid_seq; Type: SEQUENCE; Schema: public; Owner: compexe_admin
--

CREATE SEQUENCE public.usermocktestattempts_attemptid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.usermocktestattempts_attemptid_seq OWNER TO compexe_admin;

--
-- Name: usermocktestattempts_attemptid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: compexe_admin
--

ALTER SEQUENCE public.usermocktestattempts_attemptid_seq OWNED BY public.usermocktestattempts.attemptid;


--
-- Name: users; Type: TABLE; Schema: public; Owner: compexe_admin
--

CREATE TABLE public.users (
    userid integer NOT NULL,
    username character varying(50) NOT NULL,
    password character varying(100) NOT NULL,
    email character varying(100) NOT NULL,
    registrationdate timestamp(6) without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.users OWNER TO compexe_admin;

--
-- Name: users_userid_seq; Type: SEQUENCE; Schema: public; Owner: compexe_admin
--

CREATE SEQUENCE public.users_userid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_userid_seq OWNER TO compexe_admin;

--
-- Name: users_userid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: compexe_admin
--

ALTER SEQUENCE public.users_userid_seq OWNED BY public.users.userid;


--
-- Name: userstreaks; Type: TABLE; Schema: public; Owner: compexe_admin
--

CREATE TABLE public.userstreaks (
    streakid integer NOT NULL,
    userid integer,
    currentstreak integer DEFAULT 0,
    lasttestdate date,
    higheststreak integer DEFAULT 0
);


ALTER TABLE public.userstreaks OWNER TO compexe_admin;

--
-- Name: userstreaks_streakid_seq; Type: SEQUENCE; Schema: public; Owner: compexe_admin
--

CREATE SEQUENCE public.userstreaks_streakid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.userstreaks_streakid_seq OWNER TO compexe_admin;

--
-- Name: userstreaks_streakid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: compexe_admin
--

ALTER SEQUENCE public.userstreaks_streakid_seq OWNED BY public.userstreaks.streakid;


--
-- Name: ProblemsSet problemsSetId; Type: DEFAULT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public."ProblemsSet" ALTER COLUMN "problemsSetId" SET DEFAULT nextval('public."ProblemsSet_problemsSetId_seq"'::regclass);


--
-- Name: examtypes examtypeid; Type: DEFAULT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.examtypes ALTER COLUMN examtypeid SET DEFAULT nextval('public.examtypes_examtypeid_seq'::regclass);


--
-- Name: mocksections mocksectionid; Type: DEFAULT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.mocksections ALTER COLUMN mocksectionid SET DEFAULT nextval('public.mocksections_mocksectionid_seq'::regclass);


--
-- Name: mocktestrankings rankingid; Type: DEFAULT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.mocktestrankings ALTER COLUMN rankingid SET DEFAULT nextval('public.mocktestrankings_rankingid_seq'::regclass);


--
-- Name: mocktests mocktestid; Type: DEFAULT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.mocktests ALTER COLUMN mocktestid SET DEFAULT nextval('public.mocktests_mocktestid_seq'::regclass);


--
-- Name: mocktestsectionscores scoreid; Type: DEFAULT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.mocktestsectionscores ALTER COLUMN scoreid SET DEFAULT nextval('public.mocktestsectionscores_scoreid_seq'::regclass);


--
-- Name: problemoptions optionid; Type: DEFAULT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.problemoptions ALTER COLUMN optionid SET DEFAULT nextval('public.problemoptions_optionid_seq'::regclass);


--
-- Name: problems problemid; Type: DEFAULT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.problems ALTER COLUMN problemid SET DEFAULT nextval('public.problems_problemid_seq'::regclass);


--
-- Name: sections sectionid; Type: DEFAULT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.sections ALTER COLUMN sectionid SET DEFAULT nextval('public.sections_sectionid_seq'::regclass);


--
-- Name: tags tagid; Type: DEFAULT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.tags ALTER COLUMN tagid SET DEFAULT nextval('public.tags_tagid_seq'::regclass);


--
-- Name: userattempt_selectedoptions id; Type: DEFAULT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.userattempt_selectedoptions ALTER COLUMN id SET DEFAULT nextval('public.userattempt_selectedoptions_id_seq'::regclass);


--
-- Name: userattempts attemptid; Type: DEFAULT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.userattempts ALTER COLUMN attemptid SET DEFAULT nextval('public.userattempts_attemptid_seq'::regclass);


--
-- Name: usermocktestattempts attemptid; Type: DEFAULT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.usermocktestattempts ALTER COLUMN attemptid SET DEFAULT nextval('public.usermocktestattempts_attemptid_seq'::regclass);


--
-- Name: users userid; Type: DEFAULT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.users ALTER COLUMN userid SET DEFAULT nextval('public.users_userid_seq'::regclass);


--
-- Name: userstreaks streakid; Type: DEFAULT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.userstreaks ALTER COLUMN streakid SET DEFAULT nextval('public.userstreaks_streakid_seq'::regclass);


--
-- Data for Name: ProblemsSet; Type: TABLE DATA; Schema: public; Owner: compexe_admin
--

COPY public."ProblemsSet" ("problemsSetId", sectionid, examtypeid, title, type, content, mocksectionid, mockquestionnumber) FROM stdin;
51	4	2	Exploring the Frontiers of Physical Sciences: Thermodynamics, Quantum Mechanics, and Electromagnetism	RC	{"passages": ["The study of thermodynamics, a fundamental branch of physics, delves into the principles governing energy transfer and the transformations it undergoes. It is critical for understanding both macroscopic systems, such as engines and refrigerators, and microscopic phenomena, including molecular interactions. One of the cornerstone concepts is the first law of thermodynamics, which asserts that energy cannot be created or destroyed, only converted from one form to another. This principle is not only applicable to theoretical scenarios but also crucial in real-world applications. Through the lens of thermodynamics, phenomena such as entropy reveal the tendency towards disorder in energy systems. Understanding these principles is essential for advancements in technology, particularly in areas like renewable energy and materials science.", "Quantum mechanics, a pivotal theory in physics, fundamentally redefined our comprehension of matter and energy at the smallest scales. Central to quantum mechanics is the concept of wave-particle duality, which posits that particles can exhibit both wave-like and particle-like behaviors depending on the experimental setup. This is exemplified in the famous double-slit experiment, where light behaves as both a wave and a particle. Furthermore, quantum entanglement demonstrates the intricate connections between particles across vast distances, leading to the puzzling idea that the state of one particle can instantaneously affect another, regardless of the space separating them. These phenomena challenge classical intuitions, prompting a reconsideration of the nature of reality and its inherent limitations. The implications of quantum mechanics extend far beyond theoretical implications, influencing the development of technologies such as semiconductors and quantum computers, which hold the potential to revolutionize information processing.", "The principles of electromagnetism play a vital role in both theoretical physics and practical applications, bridging the gap between electric and magnetic fields. Established by James Clerk Maxwell in the 19th century, Maxwell's equations describe how electric charges create electric fields and how changing magnetic fields generate electric currents. This interconnectivity is the foundation for understanding technologies including electric motors, generators, and wireless communication. One of the intriguing aspects of electromagnetism is the concept of electromagnetic waves, which propagate through space and are responsible for various phenomena such as light and radio waves. The implications of this theory extend into modern technologies, with applications in medical imaging through MRI and the use of lasers in various fields. As we delve deeper into electromagnetism, it embodies the unification of forces that govern both everyday life and advanced scientific phenomena, illustrating the profound interrelations of the physical universe."]}	33	10
52	4	2	Interconnected Realities: Exploring the Frontiers of Physical Sciences	RC	{"passages": ["In the study of physical sciences, the interactions between matter and energy reveal fundamental principles that govern the behavior of the universe. For instance, the relationship outlined by Einstein's theory of relativity indicates that energy can transform into mass, leading to the understanding that these two entities are interconnected. This relationship is not merely theoretical but has practical applications, such as in nuclear energy, where minute amounts of mass are converted into substantial energy. Moreover, the principles of thermodynamics further explicate how energy flows between systems, establishing laws that dictate heat transfer and efficiency in physical processes. By exploring these interactions, scientists can predict the outcomes of various phenomena, expanding our comprehension of both the microcosmic and macrocosmic scales of existence.", "Advancements in physical sciences have illuminated the intricate patterns underlying natural phenomena, leading to revolutionary breakthroughs. Consider the quantum theory, which challenges classical notions by suggesting that particles exist in states of superposition, allowing them to occupy multiple states simultaneously until observed. This principle significantly alters our understanding of reality, presenting a nuanced perspective where determinism is replaced by probabilities. Applied to technologies such as semiconductors and lasers, quantum mechanics has catalyzed the development of modern electronics. Furthermore, the interplay of electromagnetism and gravity reveals the cohesive forces that not only shape cosmic structures but also dictate the fabric of spacetime. Such insights foster innovations in diverse fields, bridging theoretical physics and practical applications.", "The exploration of physical sciences extends beyond mere observation; it is a pursuit of understanding the principles that underpin our reality. The standard model of particle physics encompasses the fundamental particles and forces, offering a framework that connects the macroscopic observations of the universe to the microscopic subatomic world. Through this model, scientists hypothesize the existence of the Higgs boson, a particle that endows mass to others through the Higgs field, thus providing insight into why matter has mass. In addition, thermodynamic principles elucidate the behavior of systems in equilibrium and the directionality of energy transformations. Through experiments and theoretical modeling, physicists strive to unify these expansive concepts, aiming to create a singular theory that encapsulates all known physical phenomena.", "To grasp the complexities of physical sciences, one must consider the role of interdisciplinary research, which integrates principles from chemistry, biology, and environmental science. Recent investigations into climate change illustrate the intricate dynamics between human activity and natural systems, emphasizing the need for a comprehensive understanding of feedback loops and tipping points. For example, the increase of greenhouse gases not only raises global temperatures but also affects ocean currents and weather patterns, revealing interdependencies inherent to Earth's systems. This complexity necessitates sophisticated modeling techniques that employ data from various scientific fields to predict future scenarios. By engaging in such multi-faceted studies, researchers can devise strategies aimed at mitigating adverse environmental impacts and promoting sustainability. Such an approach underscores the importance of collaboration among scientists to address global challenges effectively."]}	33	11
53	4	2	Transformative Eras in History: Exploration, Renaissance, and Industrial Changes	RC	{"passages": ["Throughout history, the development of civilizations has relied heavily on the exchange of ideas, goods, and cultural practices among different societies. Trade routes, such as the Silk Road, not only facilitated the movement of products like silk and spices but also acted as conduits for the spread of religious beliefs, innovations, and languages. This intricate network of interactions significantly contributed to the enrichment of diverse cultures, leading to advancements in art, science, and philosophy. As societies engaged with one another, they shared their histories and traditions, which reflected the interconnected nature of human experience and mutual influence in shaping the modern world.", "The Renaissance, a period spanning the 14th to the 17th century, marked a profound transformation in various aspects of European society. Originating in Italy, this cultural movement emphasized a revival of learning based on classical sources, highlighting the importance of humanism. Artists, such as Leonardo da Vinci and Michelangelo, explored the intricacies of human anatomy and natural landscapes, producing masterpieces that continue to inspire awe. Furthermore, the invention of the printing press by Johannes Gutenberg revolutionized the dissemination of knowledge, enabling ideas to transcend geographical boundaries. This surge in intellectual inquiry and artistic expression laid the groundwork for the modern age, reshaping perspectives on art, science, and individual potential.", "The Age of Exploration, occurring from the late 15th to the early 17th century, was a pivotal era characterized by European nations expanding their territories and influence across the globe. Driven by a desire for new trade routes and wealth, explorers like Christopher Columbus and Vasco da Gama ventured into uncharted waters. Their voyages led to the discovery of new lands, including the Americas and sea passages to India, fundamentally altering global commerce and cultural exchanges. However, this expansion brought about significant consequences, including the colonization of indigenous populations and the establishment of the transatlantic slave trade. Thus, while the Age of Exploration expanded horizons, it also initiated complex social and ethical dilemmas that resonate to this day.", "The Industrial Revolution, which began in the late 18th century and continued into the 19th century, marked a major turning point in history. This era was characterized by the transition from agrarian economies to industrialized and urbanized societies. The introduction of machinery and technological innovations, such as the steam engine and spinning jenny, significantly increased production capacity and efficiency. Additionally, the rise of factories led to mass employment opportunities but also resulted in challenging working conditions for laborers. Urban centers expanded as people migrated for work, resulting in both socio-economic advancements and public health challenges. The ramifications of the Industrial Revolution are profound, laying the groundwork for the modern economy and influencing societal structures globally."]}	33	12
54	4	2	The Interplay of Mind, Behavior, and Technology in Modern Psychology	RC	{"passages": ["The study of psychology encompasses a vast array of topics concerned with the mind, behavior, and the complex interactions between individuals and their environments. Psychologists seek to understand not only the cognitive processes that underlie human actions but also the emotional and social factors that influence behavior. For instance, research indicates that societal norms and cultural backgrounds significantly shape an individual's self-perception and decision-making. The rise of cognitive-behavioral therapy exemplifies a paradigm shift in psychological treatment, emphasizing the interconnectedness of thought patterns, emotions, and behaviors. As such, psychologists are often tasked with tailoring interventions to meet the unique needs of diverse populations, thereby enhancing the efficacy of therapeutic practices.", "In the realm of psychology, the concept of resilience has garnered significant interest, as it pertains to an individual's capacity to adapt in the face of adversity. Research illustrates that resilient individuals often possess certain traits, such as optimism, cognitive flexibility, and robust social support networks. These attributes not only help them navigate challenging situations but also allow them to thrive under pressure. Moreover, interventions aimed at fostering resilience, such as mindfulness training and positive psychology practices, have shown promise in enhancing emotional well-being. However, the relationship between resilience and mental health is complex, as various factors, including genetics and childhood experiences, interplay to shape an individual's resilience levels. Understanding these dynamics is crucial for developing effective therapeutic strategies and promoting mental health within communities.", "The emergence of technology has profoundly influenced psychological research and practice, particularly through the advent of digital mental health tools. These innovations range from mobile applications designed for self-monitoring emotions to online therapy platforms connecting individuals with licensed therapists. The efficacy of such tools has become a focal point of contemporary studies, as they offer accessibility and convenience for a broader audience. However, questions remain about the potential drawbacks, including privacy concerns and the quality of care provided. Additionally, the integration of artificial intelligence in diagnostics and treatment raises ethical considerations, prompting discussions about the role of human empathy in psychological interventions. As technology continues to evolve, its implications for the future of psychological practice warrant careful examination and thoughtful discourse."]}	33	13
55	5	2	Balancing Technology and Workforce Development in Logistics	TPA	[{"type": "Passage", "passage": ["In recent years, the logistics and supply chain industry has undergone significant changes due to advancements in technology and shifts in consumer demand. Companies are increasingly adopting automation and artificial intelligence to enhance efficiency and reduce operational costs.", "However, implementing these technologies requires substantial investment and can pose risks if not properly managed. Companies must also consider the impact on their workforce, as automation may lead to job displacement while creating opportunities in tech-savvy roles.", "To remain competitive, organizations are expected to adopt a holistic approach, balancing technology integration with a commitment to workforce development and sustainable practices."]}]	34	6
56	5	2	Evaluating the Interrelationship Between Logistics Costs and Supply Chain Efficiency		{}	34	20
57	4	2	Exploring the Frontiers of Physical Sciences: Thermodynamics, Quantum Mechanics, and Electromagnetism	RC	{"passages": ["The study of thermodynamics, a fundamental branch of physics, delves into the principles governing energy transfer and the transformations it undergoes. It is critical for understanding both macroscopic systems, such as engines and refrigerators, and microscopic phenomena, including molecular interactions. One of the cornerstone concepts is the first law of thermodynamics, which asserts that energy cannot be created or destroyed, only converted from one form to another. This principle is not only applicable to theoretical scenarios but also crucial in real-world applications. Through the lens of thermodynamics, phenomena such as entropy reveal the tendency towards disorder in energy systems. Understanding these principles is essential for advancements in technology, particularly in areas like renewable energy and materials science.", "Quantum mechanics, a pivotal theory in physics, fundamentally redefined our comprehension of matter and energy at the smallest scales. Central to quantum mechanics is the concept of wave-particle duality, which posits that particles can exhibit both wave-like and particle-like behaviors depending on the experimental setup. This is exemplified in the famous double-slit experiment, where light behaves as both a wave and a particle. Furthermore, quantum entanglement demonstrates the intricate connections between particles across vast distances, leading to the puzzling idea that the state of one particle can instantaneously affect another, regardless of the space separating them. These phenomena challenge classical intuitions, prompting a reconsideration of the nature of reality and its inherent limitations. The implications of quantum mechanics extend far beyond theoretical implications, influencing the development of technologies such as semiconductors and quantum computers, which hold the potential to revolutionize information processing.", "The principles of electromagnetism play a vital role in both theoretical physics and practical applications, bridging the gap between electric and magnetic fields. Established by James Clerk Maxwell in the 19th century, Maxwell's equations describe how electric charges create electric fields and how changing magnetic fields generate electric currents. This interconnectivity is the foundation for understanding technologies including electric motors, generators, and wireless communication. One of the intriguing aspects of electromagnetism is the concept of electromagnetic waves, which propagate through space and are responsible for various phenomena such as light and radio waves. The implications of this theory extend into modern technologies, with applications in medical imaging through MRI and the use of lasers in various fields. As we delve deeper into electromagnetism, it embodies the unification of forces that govern both everyday life and advanced scientific phenomena, illustrating the profound interrelations of the physical universe."]}	\N	\N
58	4	2	Interconnected Realities: Exploring the Frontiers of Physical Sciences	RC	{"passages": ["In the study of physical sciences, the interactions between matter and energy reveal fundamental principles that govern the behavior of the universe. For instance, the relationship outlined by Einstein's theory of relativity indicates that energy can transform into mass, leading to the understanding that these two entities are interconnected. This relationship is not merely theoretical but has practical applications, such as in nuclear energy, where minute amounts of mass are converted into substantial energy. Moreover, the principles of thermodynamics further explicate how energy flows between systems, establishing laws that dictate heat transfer and efficiency in physical processes. By exploring these interactions, scientists can predict the outcomes of various phenomena, expanding our comprehension of both the microcosmic and macrocosmic scales of existence.", "Advancements in physical sciences have illuminated the intricate patterns underlying natural phenomena, leading to revolutionary breakthroughs. Consider the quantum theory, which challenges classical notions by suggesting that particles exist in states of superposition, allowing them to occupy multiple states simultaneously until observed. This principle significantly alters our understanding of reality, presenting a nuanced perspective where determinism is replaced by probabilities. Applied to technologies such as semiconductors and lasers, quantum mechanics has catalyzed the development of modern electronics. Furthermore, the interplay of electromagnetism and gravity reveals the cohesive forces that not only shape cosmic structures but also dictate the fabric of spacetime. Such insights foster innovations in diverse fields, bridging theoretical physics and practical applications.", "The exploration of physical sciences extends beyond mere observation; it is a pursuit of understanding the principles that underpin our reality. The standard model of particle physics encompasses the fundamental particles and forces, offering a framework that connects the macroscopic observations of the universe to the microscopic subatomic world. Through this model, scientists hypothesize the existence of the Higgs boson, a particle that endows mass to others through the Higgs field, thus providing insight into why matter has mass. In addition, thermodynamic principles elucidate the behavior of systems in equilibrium and the directionality of energy transformations. Through experiments and theoretical modeling, physicists strive to unify these expansive concepts, aiming to create a singular theory that encapsulates all known physical phenomena.", "To grasp the complexities of physical sciences, one must consider the role of interdisciplinary research, which integrates principles from chemistry, biology, and environmental science. Recent investigations into climate change illustrate the intricate dynamics between human activity and natural systems, emphasizing the need for a comprehensive understanding of feedback loops and tipping points. For example, the increase of greenhouse gases not only raises global temperatures but also affects ocean currents and weather patterns, revealing interdependencies inherent to Earth's systems. This complexity necessitates sophisticated modeling techniques that employ data from various scientific fields to predict future scenarios. By engaging in such multi-faceted studies, researchers can devise strategies aimed at mitigating adverse environmental impacts and promoting sustainability. Such an approach underscores the importance of collaboration among scientists to address global challenges effectively."]}	\N	\N
59	4	2	Transformative Eras in History: Exploration, Renaissance, and Industrial Changes	RC	{"passages": ["Throughout history, the development of civilizations has relied heavily on the exchange of ideas, goods, and cultural practices among different societies. Trade routes, such as the Silk Road, not only facilitated the movement of products like silk and spices but also acted as conduits for the spread of religious beliefs, innovations, and languages. This intricate network of interactions significantly contributed to the enrichment of diverse cultures, leading to advancements in art, science, and philosophy. As societies engaged with one another, they shared their histories and traditions, which reflected the interconnected nature of human experience and mutual influence in shaping the modern world.", "The Renaissance, a period spanning the 14th to the 17th century, marked a profound transformation in various aspects of European society. Originating in Italy, this cultural movement emphasized a revival of learning based on classical sources, highlighting the importance of humanism. Artists, such as Leonardo da Vinci and Michelangelo, explored the intricacies of human anatomy and natural landscapes, producing masterpieces that continue to inspire awe. Furthermore, the invention of the printing press by Johannes Gutenberg revolutionized the dissemination of knowledge, enabling ideas to transcend geographical boundaries. This surge in intellectual inquiry and artistic expression laid the groundwork for the modern age, reshaping perspectives on art, science, and individual potential.", "The Age of Exploration, occurring from the late 15th to the early 17th century, was a pivotal era characterized by European nations expanding their territories and influence across the globe. Driven by a desire for new trade routes and wealth, explorers like Christopher Columbus and Vasco da Gama ventured into uncharted waters. Their voyages led to the discovery of new lands, including the Americas and sea passages to India, fundamentally altering global commerce and cultural exchanges. However, this expansion brought about significant consequences, including the colonization of indigenous populations and the establishment of the transatlantic slave trade. Thus, while the Age of Exploration expanded horizons, it also initiated complex social and ethical dilemmas that resonate to this day.", "The Industrial Revolution, which began in the late 18th century and continued into the 19th century, marked a major turning point in history. This era was characterized by the transition from agrarian economies to industrialized and urbanized societies. The introduction of machinery and technological innovations, such as the steam engine and spinning jenny, significantly increased production capacity and efficiency. Additionally, the rise of factories led to mass employment opportunities but also resulted in challenging working conditions for laborers. Urban centers expanded as people migrated for work, resulting in both socio-economic advancements and public health challenges. The ramifications of the Industrial Revolution are profound, laying the groundwork for the modern economy and influencing societal structures globally."]}	\N	\N
60	4	2	The Interplay of Mind, Behavior, and Technology in Modern Psychology	RC	{"passages": ["The study of psychology encompasses a vast array of topics concerned with the mind, behavior, and the complex interactions between individuals and their environments. Psychologists seek to understand not only the cognitive processes that underlie human actions but also the emotional and social factors that influence behavior. For instance, research indicates that societal norms and cultural backgrounds significantly shape an individual's self-perception and decision-making. The rise of cognitive-behavioral therapy exemplifies a paradigm shift in psychological treatment, emphasizing the interconnectedness of thought patterns, emotions, and behaviors. As such, psychologists are often tasked with tailoring interventions to meet the unique needs of diverse populations, thereby enhancing the efficacy of therapeutic practices.", "In the realm of psychology, the concept of resilience has garnered significant interest, as it pertains to an individual's capacity to adapt in the face of adversity. Research illustrates that resilient individuals often possess certain traits, such as optimism, cognitive flexibility, and robust social support networks. These attributes not only help them navigate challenging situations but also allow them to thrive under pressure. Moreover, interventions aimed at fostering resilience, such as mindfulness training and positive psychology practices, have shown promise in enhancing emotional well-being. However, the relationship between resilience and mental health is complex, as various factors, including genetics and childhood experiences, interplay to shape an individual's resilience levels. Understanding these dynamics is crucial for developing effective therapeutic strategies and promoting mental health within communities.", "The emergence of technology has profoundly influenced psychological research and practice, particularly through the advent of digital mental health tools. These innovations range from mobile applications designed for self-monitoring emotions to online therapy platforms connecting individuals with licensed therapists. The efficacy of such tools has become a focal point of contemporary studies, as they offer accessibility and convenience for a broader audience. However, questions remain about the potential drawbacks, including privacy concerns and the quality of care provided. Additionally, the integration of artificial intelligence in diagnostics and treatment raises ethical considerations, prompting discussions about the role of human empathy in psychological interventions. As technology continues to evolve, its implications for the future of psychological practice warrant careful examination and thoughtful discourse."]}	\N	\N
61	5	2	Balancing Technology and Workforce Development in Logistics	TPA	[{"type": "Passage", "passage": ["In recent years, the logistics and supply chain industry has undergone significant changes due to advancements in technology and shifts in consumer demand. Companies are increasingly adopting automation and artificial intelligence to enhance efficiency and reduce operational costs.", "However, implementing these technologies requires substantial investment and can pose risks if not properly managed. Companies must also consider the impact on their workforce, as automation may lead to job displacement while creating opportunities in tech-savvy roles.", "To remain competitive, organizations are expected to adopt a holistic approach, balancing technology integration with a commitment to workforce development and sustainable practices."]}]	\N	\N
62	5	2	Evaluating the Interrelationship Between Logistics Costs and Supply Chain Efficiency		{}	\N	\N
63	4	2	Exploring the Frontiers of Physical Sciences: Thermodynamics, Quantum Mechanics, and Electromagnetism	RC	{"passages": ["The study of thermodynamics, a fundamental branch of physics, delves into the principles governing energy transfer and the transformations it undergoes. It is critical for understanding both macroscopic systems, such as engines and refrigerators, and microscopic phenomena, including molecular interactions. One of the cornerstone concepts is the first law of thermodynamics, which asserts that energy cannot be created or destroyed, only converted from one form to another. This principle is not only applicable to theoretical scenarios but also crucial in real-world applications. Through the lens of thermodynamics, phenomena such as entropy reveal the tendency towards disorder in energy systems. Understanding these principles is essential for advancements in technology, particularly in areas like renewable energy and materials science.", "Quantum mechanics, a pivotal theory in physics, fundamentally redefined our comprehension of matter and energy at the smallest scales. Central to quantum mechanics is the concept of wave-particle duality, which posits that particles can exhibit both wave-like and particle-like behaviors depending on the experimental setup. This is exemplified in the famous double-slit experiment, where light behaves as both a wave and a particle. Furthermore, quantum entanglement demonstrates the intricate connections between particles across vast distances, leading to the puzzling idea that the state of one particle can instantaneously affect another, regardless of the space separating them. These phenomena challenge classical intuitions, prompting a reconsideration of the nature of reality and its inherent limitations. The implications of quantum mechanics extend far beyond theoretical implications, influencing the development of technologies such as semiconductors and quantum computers, which hold the potential to revolutionize information processing.", "The principles of electromagnetism play a vital role in both theoretical physics and practical applications, bridging the gap between electric and magnetic fields. Established by James Clerk Maxwell in the 19th century, Maxwell's equations describe how electric charges create electric fields and how changing magnetic fields generate electric currents. This interconnectivity is the foundation for understanding technologies including electric motors, generators, and wireless communication. One of the intriguing aspects of electromagnetism is the concept of electromagnetic waves, which propagate through space and are responsible for various phenomena such as light and radio waves. The implications of this theory extend into modern technologies, with applications in medical imaging through MRI and the use of lasers in various fields. As we delve deeper into electromagnetism, it embodies the unification of forces that govern both everyday life and advanced scientific phenomena, illustrating the profound interrelations of the physical universe."]}	\N	\N
64	4	2	Interconnected Realities: Exploring the Frontiers of Physical Sciences	RC	{"passages": ["In the study of physical sciences, the interactions between matter and energy reveal fundamental principles that govern the behavior of the universe. For instance, the relationship outlined by Einstein's theory of relativity indicates that energy can transform into mass, leading to the understanding that these two entities are interconnected. This relationship is not merely theoretical but has practical applications, such as in nuclear energy, where minute amounts of mass are converted into substantial energy. Moreover, the principles of thermodynamics further explicate how energy flows between systems, establishing laws that dictate heat transfer and efficiency in physical processes. By exploring these interactions, scientists can predict the outcomes of various phenomena, expanding our comprehension of both the microcosmic and macrocosmic scales of existence.", "Advancements in physical sciences have illuminated the intricate patterns underlying natural phenomena, leading to revolutionary breakthroughs. Consider the quantum theory, which challenges classical notions by suggesting that particles exist in states of superposition, allowing them to occupy multiple states simultaneously until observed. This principle significantly alters our understanding of reality, presenting a nuanced perspective where determinism is replaced by probabilities. Applied to technologies such as semiconductors and lasers, quantum mechanics has catalyzed the development of modern electronics. Furthermore, the interplay of electromagnetism and gravity reveals the cohesive forces that not only shape cosmic structures but also dictate the fabric of spacetime. Such insights foster innovations in diverse fields, bridging theoretical physics and practical applications.", "The exploration of physical sciences extends beyond mere observation; it is a pursuit of understanding the principles that underpin our reality. The standard model of particle physics encompasses the fundamental particles and forces, offering a framework that connects the macroscopic observations of the universe to the microscopic subatomic world. Through this model, scientists hypothesize the existence of the Higgs boson, a particle that endows mass to others through the Higgs field, thus providing insight into why matter has mass. In addition, thermodynamic principles elucidate the behavior of systems in equilibrium and the directionality of energy transformations. Through experiments and theoretical modeling, physicists strive to unify these expansive concepts, aiming to create a singular theory that encapsulates all known physical phenomena.", "To grasp the complexities of physical sciences, one must consider the role of interdisciplinary research, which integrates principles from chemistry, biology, and environmental science. Recent investigations into climate change illustrate the intricate dynamics between human activity and natural systems, emphasizing the need for a comprehensive understanding of feedback loops and tipping points. For example, the increase of greenhouse gases not only raises global temperatures but also affects ocean currents and weather patterns, revealing interdependencies inherent to Earth's systems. This complexity necessitates sophisticated modeling techniques that employ data from various scientific fields to predict future scenarios. By engaging in such multi-faceted studies, researchers can devise strategies aimed at mitigating adverse environmental impacts and promoting sustainability. Such an approach underscores the importance of collaboration among scientists to address global challenges effectively."]}	\N	\N
65	4	2	Transformative Eras in History: Exploration, Renaissance, and Industrial Changes	RC	{"passages": ["Throughout history, the development of civilizations has relied heavily on the exchange of ideas, goods, and cultural practices among different societies. Trade routes, such as the Silk Road, not only facilitated the movement of products like silk and spices but also acted as conduits for the spread of religious beliefs, innovations, and languages. This intricate network of interactions significantly contributed to the enrichment of diverse cultures, leading to advancements in art, science, and philosophy. As societies engaged with one another, they shared their histories and traditions, which reflected the interconnected nature of human experience and mutual influence in shaping the modern world.", "The Renaissance, a period spanning the 14th to the 17th century, marked a profound transformation in various aspects of European society. Originating in Italy, this cultural movement emphasized a revival of learning based on classical sources, highlighting the importance of humanism. Artists, such as Leonardo da Vinci and Michelangelo, explored the intricacies of human anatomy and natural landscapes, producing masterpieces that continue to inspire awe. Furthermore, the invention of the printing press by Johannes Gutenberg revolutionized the dissemination of knowledge, enabling ideas to transcend geographical boundaries. This surge in intellectual inquiry and artistic expression laid the groundwork for the modern age, reshaping perspectives on art, science, and individual potential.", "The Age of Exploration, occurring from the late 15th to the early 17th century, was a pivotal era characterized by European nations expanding their territories and influence across the globe. Driven by a desire for new trade routes and wealth, explorers like Christopher Columbus and Vasco da Gama ventured into uncharted waters. Their voyages led to the discovery of new lands, including the Americas and sea passages to India, fundamentally altering global commerce and cultural exchanges. However, this expansion brought about significant consequences, including the colonization of indigenous populations and the establishment of the transatlantic slave trade. Thus, while the Age of Exploration expanded horizons, it also initiated complex social and ethical dilemmas that resonate to this day.", "The Industrial Revolution, which began in the late 18th century and continued into the 19th century, marked a major turning point in history. This era was characterized by the transition from agrarian economies to industrialized and urbanized societies. The introduction of machinery and technological innovations, such as the steam engine and spinning jenny, significantly increased production capacity and efficiency. Additionally, the rise of factories led to mass employment opportunities but also resulted in challenging working conditions for laborers. Urban centers expanded as people migrated for work, resulting in both socio-economic advancements and public health challenges. The ramifications of the Industrial Revolution are profound, laying the groundwork for the modern economy and influencing societal structures globally."]}	\N	\N
66	4	2	The Interplay of Mind, Behavior, and Technology in Modern Psychology	RC	{"passages": ["The study of psychology encompasses a vast array of topics concerned with the mind, behavior, and the complex interactions between individuals and their environments. Psychologists seek to understand not only the cognitive processes that underlie human actions but also the emotional and social factors that influence behavior. For instance, research indicates that societal norms and cultural backgrounds significantly shape an individual's self-perception and decision-making. The rise of cognitive-behavioral therapy exemplifies a paradigm shift in psychological treatment, emphasizing the interconnectedness of thought patterns, emotions, and behaviors. As such, psychologists are often tasked with tailoring interventions to meet the unique needs of diverse populations, thereby enhancing the efficacy of therapeutic practices.", "In the realm of psychology, the concept of resilience has garnered significant interest, as it pertains to an individual's capacity to adapt in the face of adversity. Research illustrates that resilient individuals often possess certain traits, such as optimism, cognitive flexibility, and robust social support networks. These attributes not only help them navigate challenging situations but also allow them to thrive under pressure. Moreover, interventions aimed at fostering resilience, such as mindfulness training and positive psychology practices, have shown promise in enhancing emotional well-being. However, the relationship between resilience and mental health is complex, as various factors, including genetics and childhood experiences, interplay to shape an individual's resilience levels. Understanding these dynamics is crucial for developing effective therapeutic strategies and promoting mental health within communities.", "The emergence of technology has profoundly influenced psychological research and practice, particularly through the advent of digital mental health tools. These innovations range from mobile applications designed for self-monitoring emotions to online therapy platforms connecting individuals with licensed therapists. The efficacy of such tools has become a focal point of contemporary studies, as they offer accessibility and convenience for a broader audience. However, questions remain about the potential drawbacks, including privacy concerns and the quality of care provided. Additionally, the integration of artificial intelligence in diagnostics and treatment raises ethical considerations, prompting discussions about the role of human empathy in psychological interventions. As technology continues to evolve, its implications for the future of psychological practice warrant careful examination and thoughtful discourse."]}	\N	\N
67	5	2	Balancing Technology and Workforce Development in Logistics	TPA	[{"type": "Passage", "passage": ["In recent years, the logistics and supply chain industry has undergone significant changes due to advancements in technology and shifts in consumer demand. Companies are increasingly adopting automation and artificial intelligence to enhance efficiency and reduce operational costs.", "However, implementing these technologies requires substantial investment and can pose risks if not properly managed. Companies must also consider the impact on their workforce, as automation may lead to job displacement while creating opportunities in tech-savvy roles.", "To remain competitive, organizations are expected to adopt a holistic approach, balancing technology integration with a commitment to workforce development and sustainable practices."]}]	\N	\N
68	5	2	Evaluating the Interrelationship Between Logistics Costs and Supply Chain Efficiency		{}	\N	\N
69	1	1	Analyzing the Relationship Between Principal Amount, Interest Rates, and Interest Earned	PS	[{"type": "scatter plot", "graph": {"data": [{"x": 1000, "y": 50}, {"x": 2000, "y": 100}, {"x": 3000, "y": 150}, {"x": 4000, "y": 200}, {"x": 5000, "y": 250}], "title": "Impact of Principal on Interest Earned", "xAxis": "Principal Amount (in $)", "yAxis": "Total Interest Earned (in $)"}, "description": "This scatter plot illustrates how the principal amount affects the total interest earned over time."}, {"type": "scatter plot", "graph": {"data": [{"x": 1, "y": 50}, {"x": 2, "y": 100}, {"x": 3, "y": 150}, {"x": 4, "y": 200}, {"x": 5, "y": 300}], "title": "Effect of Rate of Interest on Total Gain", "xAxis": "Rate of Interest (%)", "yAxis": "Total Gain (in $)"}, "description": "This scatter plot demonstrates the effect of varying interest rates on the total gain over time."}]	35	8
70	1	1	Analysis of Logistics Operations and Their Cost Distribution	PS	[{"type": "pie chart", "graph": {"data": [{"name": "Fuel", "color": "#FF5733", "value": 25}, {"name": "Labor", "color": "#33FF57", "value": 35}, {"name": "Maintenance", "color": "#3357FF", "value": 20}, {"name": "Administrative", "color": "#F0C33F", "value": 20}], "title": "Distribution of Logistics Costs"}, "description": "This pie chart illustrates the percentage distribution of various logistics costs within a company."}, {"type": "line graph", "graph": {"data": {"data": [15000, 20000, 18000, 22000, 30000, 35000, 48000, 47000, 42000, 32000, 18000, 20000], "x-axis": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], "y-axis": [0, 5000, 10000, 15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000, 55000]}, "title": "Monthly Logistics Expenses over a Year", "xAxis": "Months", "yAxis": "Expenses (in USD)"}, "description": "This line graph presents the monthly logistics expenses incurred by a company over the span of a year."}, {"type": "pie chart", "graph": {"data": [{"name": "Air", "color": "#FF8C00", "value": 40}, {"name": "Sea", "color": "#00FF8C", "value": 30}, {"name": "Land", "color": "#8C00FF", "value": 30}], "title": "Proportion of Shipping Methods Used"}, "description": "This pie chart depicts the distribution of shipping methods utilized by the logistics company."}]	35	9
71	1	1	Analysis of Employee Turnover, Satisfaction, and Recruitment Effectiveness	PS	[{"type": "bar graph", "graph": {"data": {"data": [15, 10, 5, 20, 12], "x-axis": ["Sales", "Marketing", "IT", "HR", "Finance"], "y-axis": [0, 5, 10, 15, 20]}, "title": "Employee Turnover Rates Across Departments", "xAxis": "Departments", "yAxis": "Turnover Rate (%)"}, "description": "This bar graph illustrates the employee turnover rates across various departments within the organization, providing insights into areas that may require attention regarding employee retention."}, {"type": "bar graph", "graph": {"data": {"data": [70, 60, 80, 50, 75], "x-axis": ["Sales", "Marketing", "IT", "HR", "Finance"], "y-axis": [0, 20, 40, 60, 80, 100]}, "title": "Employee Satisfaction Scores by Department", "xAxis": "Departments", "yAxis": "Satisfaction Score (out of 100)"}, "description": "This bar graph displays the employee satisfaction scores for different departments, which can be useful for understanding the overall morale and engagement levels of employees in these areas."}, {"type": "bar graph", "graph": {"data": {"data": [80, 50, 20, 70], "x-axis": ["Referrals", "Job Boards", "Social Media", "Recruitment Agencies"], "y-axis": [0, 25, 50, 75, 100]}, "title": "Recruitment Success Rates by Source", "xAxis": "Recruitment Sources", "yAxis": "Success Rate (%)"}, "description": "This bar graph presents the recruitment success rates categorized by the source of recruitment, helping HR to assess the effectiveness of various recruitment strategies."}]	36	9
72	1	1	Exploring the Probabilities of Success in Scientific Experiments	PS	[{"rows": [{"data": ["Experiment 1", 0.86], "highlight": true}, {"data": ["Experiment 2", 0.39], "highlight": false}, {"data": ["Experiment 3", 0.41], "highlight": false}, {"data": ["Experiment 4", 0.33], "highlight": false}, {"data": ["Experiment 5", 0.59], "highlight": true}], "type": "highlight table", "headers": ["Experiment", "Probability of Success"], "description": "This highlight table displays different experiments alongside their respective probabilities of success. The entries with probabilities greater than 0.5 are highlighted to indicate higher likelihoods of success."}, {"type": "line graph", "graph": {"data": {"data": [0.86, 0.39, 0.41, 0.33, 0.59], "x-axis": [1, 2, 3, 4, 5], "y-axis": [0.86, 0.39, 0.41, 0.33, 0.59]}, "title": "Probability of Success in Different Experiments", "xAxis": "Experiment Number", "yAxis": "Probability of Success"}, "description": "This line graph illustrates the probabilities of success for different experiments. The trends in the graph provide insights into how the likelihood of success varies between experiments."}]	36	10
73	1	1	Analyzing Employee Turnover and Budget Allocation Across Different Departments in Human Resources	PS	[{"rows": [["Sales", 50, 15], ["Marketing", 30, 10], ["IT", 40, 5], ["HR", 20, 20], ["Finance", 25, 10]], "type": "standard data table", "headers": ["Department", "Employees", "Turnover Rate (%)"], "description": "This standard data table presents the number of employees and their respective turnover rates for different departments within a company."}, {"rows": [["Sales", 60000, 25], ["Marketing", 55000, 20], ["IT", 80000, 35], ["HR", 50000, 10], ["Finance", 75000, 10]], "type": "standard data table", "headers": ["Department", "Average Salary (USD)", "Budget Allocation (%)"], "description": "This standard data table provides information on the average salary of employees and the budget allocation for different departments in the organization."}]	36	11
74	2	1	Navigating the Complexities of Modern Economic Change	RC	{"passages": ["<p>In contemporary economic discourse, the debate surrounding the concept of universal basic income (UBI) has gained substantial momentum. Proponents argue that UBI could alleviate poverty and reduce income inequality by providing all citizens with a fixed, unconditional cash payment. This, they assert, would empower individuals to pursue education and vocational training without the immediate pressure of financial instability. On the other hand, opponents caution against the potential negative ramifications of UBI, including disincentivizing work and leading to unsustainable public expenditure. They contend that while the intention to bolster social welfare is commendable, the execution of such a policy must account for the intricate dynamics of labor markets and fiscal responsibilities.</p><p>Furthermore, empirical evidence from trials conducted in various nations presents a mixed bag of outcomes. Countries like Finland and Canada have experimented with UBI-like programs, which yielded promising improvements in well-being; however, critics maintain that these pilot programs lacked the scale necessary to draw definitive conclusions regarding long-term impacts on employment rates and economic productivity. Thus, as governments grapple with the quest for innovative solutions to economic disparities, the viability of UBI remains a critical, if contentious, subject worthy of in-depth analysis.</p>", "<p>The relationship between inflation and unemployment has long puzzled economists, commonly referred to as the Phillips Curve, which postulates an inverse relationship between these two variables. As inflation rises, unemployment is theorized to fall, suggesting that increasing demand in an economy leads to job creation. However, the late 20th century witnessed phenomena that challenged this correlation, notably during the era of stagflation—where high inflation coexisted with high unemployment—calling into question the validity of the Phillips Curve as an overarching principle.</p><p>Recent studies have indicated that the connection between inflation and unemployment may be more intricate than previously thought. Factors such as global supply chains, technological advancements, and changing consumer behaviors have introduced complexities that dilute the predictable nature of this relationship. Central banks, tasked with maintaining economic stability, must navigate these shifting dynamics carefully, employing monetary policies that not only aim to manage inflation but also promote a healthy labor market. The ongoing exploration of this relationship underscores the need for a more nuanced understanding of the factors influencing economic conditions, rather than relying on traditional models alone.</p>", "<p>Globalization has fundamentally transformed economic landscapes across nations, fostering deeper integration of markets, peoples, and cultures. This interconnectedness offers myriad advantages, such as expanded access to goods and services, enhanced competition, and the potential for economic growth. However, the benefits of globalization are not universally experienced; many critics argue that it disproportionately advantages developed nations while exacerbating inequalities in developing regions. This disparity raises critical questions about the sustainability of globalization as a driving force of economic progress.</p><p>Moreover, recent trends suggest a growing backlash against globalization. The rise of protectionist policies and trade wars indicates a shifting sentiment among populations who feel marginalized by rapid economic changes. Issues such as job loss due to outsourcing and the perceived erosion of cultural identities contribute to this resistance. As policymakers consider the implications of globalization, it becomes essential to balance economic integration with strategies that address the concerns of individuals and communities that may be left behind in this global economic framework. Ultimately, the future of globalization may hinge on its ability to adapt and respond to these emerging challenges while still fostering economic growth.</p>"]}	37	6
75	2	1	Exploring the Multifaceted Nature of Psychology	RC	{"passages": ["<p>Psychology, the scientific study of behavior and mental processes, is a multifaceted discipline that encompasses various subfields. Among these, cognitive psychology investigates internal mental processes such as perception, memory, and problem-solving. It examines how people understand, diagnose, and respond to the world around them. The findings of cognitive psychology have significant implications, not only advancing our understanding of the human mind but also enhancing practical applications in education, therapy, and artificial intelligence. For instance, techniques developed from cognitive psychology can improve learning strategies, aid in the treatment of cognitive impairments, and inform the design of user-friendly technology.</p><p>Behaviorism, another key subfield, emphasizes the study of observable behaviors rather than internal mental states. By focusing on how environment influences behavior through conditioning, behaviorists believe that behaviors can be measured and modified. This perspective has led to numerous practical applications, such as behavior modification therapies, which are used to address various psychological disorders. Furthermore, the integration of cognitive and behavioral approaches has given rise to cognitive-behavioral therapy (CBT), a prevalent form of treatment that addresses negative thought patterns and maladaptive behaviors.</p>", "<p>Another vital area of psychology is developmental psychology, which studies the psychological growth of individuals across their lifespan. Developmental psychologists explore how genetic and environmental factors influence cognitive, emotional, and social development. Research in this field has highlighted crucial stages, from infancy through old age, revealing how experiences shape behavior and personality. For example, attachment theory, which examines the bonds between infants and caregivers, has demonstrated how early relationships can affect emotional well-being and relationship styles throughout life.</p><p>Social psychology, on the other hand, focuses on how individuals interact and are influenced by others. This subfield explores topics such as group dynamics, conformity, and social perception, providing insights into how societal and cultural contexts shape behavior. Experiments like the Stanford prison experiment illustrate the dramatic effects of situational influences on individual actions, raising ethical considerations about psychological research. Together, these varied branches reflect the complexity of human behavior, underlining the importance of an integrated approach to understanding the mind.</p>", "<p>Another essential aspect of psychology is the study of abnormal psychology, which delves into the nature of psychological disorders, their causes, and treatments. This field identifies various mental health conditions, such as anxiety disorders, mood disorders, and personality disorders, and seeks to understand their origins and manifestations. Psychologists employ various models, including biological, psychological, and sociocultural frameworks, to explain how these disorders develop. For instance, the biopsychosocial model emphasizes the interplay of genetic predisposition, individual psychology, and environmental factors in the emergence of mental health issues.</p><p>Treatment approaches in abnormal psychology have evolved significantly over the years. Historically, those with mental illness were often subjected to harsh treatments or stigmatized. However, modern psychology advocates for evidence-based therapies, including psychotherapy and pharmacotherapy, aimed at improving the quality of life for individuals affected by mental disorders. Cognitive-behavioral therapy (CBT), for instance, is frequently employed to modify distorted thinking patterns, helping patients develop healthier coping mechanisms. Through ongoing research and practice, the understanding and treatment of mental health conditions continue to advance, challenging societal perceptions that have long surrounded psychological disorders.</p>", "<p>The field of psychology also encompasses positive psychology, a relatively recent shift in focus that emphasizes the study of optimal human functioning and well-being. This subfield encourages a proactive approach to mental health, exploring factors that contribute to happiness, resilience, and personal fulfillment. Researchers such as Martin Seligman, a pioneer in positive psychology, advocate for interventions that foster strengths, cultivate positive emotions, and enhance overall life satisfaction. Techniques such as gratitude journaling and mindfulness meditation have been shown to significantly improve psychological well-being, highlighting the importance of an affirmative perspective in psychological practice.</p><p>Moreover, industrial-organizational psychology applies psychological principles to workplace environments, aiming to enhance productivity, job satisfaction, and employee well-being. This branch tackles issues such as personnel selection, training, and organizational culture, drawing from the rich body of psychological research to improve workplace dynamics. Understanding employee motivation, teamwork, and leadership styles can lead to more effective organizations and a healthier work-life balance for individuals. Through the integration of various psychological principles, professionals can shape environments that not only foster productivity but also promote psychological well-being.</p>"]}	37	7
76	2	1	The Pursuit of Dreams and the Cost of Regret	RC	{"passages": ["<p>In his poignant novel, `The Remains of the Day`, Kazuo Ishiguro explores themes of memory and regret through the eyes of Stevens, an unyielding butler. Set in post-World War II England, the narrative unfolds as Stevens embarks on a road trip to revisit a former colleague, Miss Kenton. Through his introspective journey, readers are invited to reflect on the choices that define a life devoted to duty over personal happiness. The butler's meticulous recounting of past events reveals how the sacrifices he made in service have left him estranged from his emotions and the very joy of living.</p><p>As Stevens reminisces about his years at Darlington Hall, the dichotomy between his professional facade and personal longing becomes evident. His steadfast dedication to his role casts a shadow on his ability to form genuine connections, particularly with Miss Kenton. Ishiguro's use of subtle irony highlights the tragic irony of Stevens' life: although he prides himself on his unwavering loyalty, he ultimately realizes that such fidelity may have cost him the love he sought to protect.</p>", "<p>In `The Great Gatsby`, F. Scott Fitzgerald masterfully captures the essence of the American Dream and its disillusionment through the character of Jay Gatsby. Set in the opulence of the Roaring Twenties, the novel tells the story of Gatsby’s unwavering pursuit of wealth and status as a means to win back his lost love, Daisy Buchanan. However, Fitzgerald weaves a narrative that critiques this dream, illustrating how the quest for materialism can lead to profound emptiness and despair.</p><p>Gatsby's lavish parties and extravagant lifestyle serve as a façade, masking the underlying loneliness and moral decay that permeate his world. Through the eyes of narrator Nick Carraway, readers witness the stark contrasts between the glamorous exterior of the Jazz Age and the harsh realities that lie beneath. The green light at the end of Daisy's dock symbolizes Gatsby's unattainable dream, representing not only his aspirations but also the broader American ideal that remains perpetually out of reach for so many.</p>"]}	38	7
77	2	1	The Enduring Legacy of Ancient Civilizations	RC	{"passages": ["<p>The history of ancient civilizations has fascinated scholars and historians for centuries. One of the most remarkable aspects of these societies is their ability to develop complex social structures and cultural achievements despite the technological limitations of their time. For instance, the Mesopotamians, often regarded as the cradle of civilization, implemented one of the first known systems of writing, cuneiform, which allowed them to maintain records and communicate across distances. This innovation laid a foundation for the administrative frameworks that would support the growth of city-states.</p><p>Similarly, ancient Egypt's monumental achievements in architecture, such as the construction of the pyramids, highlight the Egyptians' advanced understanding of engineering and labor organization. These structures served not only as tombs for pharaohs but also as symbols of their power and devotion to the afterlife. Within this context, understanding the motivations behind such monumental projects provides insight into the values and beliefs of these early societies, illustrating their profound impact on the course of human history.</p>", "<p>The study of ancient Greece reveals a civilization marked by significant contributions to the arts, philosophy, and governance. The Greek city-states, particularly Athens and Sparta, developed unique political systems that influenced future governance models. Athens is celebrated for its early form of democracy, where citizens participated in decision-making processes. This pioneering system emphasized the importance of civic engagement and has informed democratic theories ever since.</p><p>In addition to politics, ancient Greece was renowned for its philosophers, such as Socrates, Plato, and Aristotle, who laid the groundwork for Western philosophy. Their inquiries into ethics, metaphysics, and politics continue to resonate today, highlighting the lasting legacy of Greek thought. The works produced during this period not only addressed the nature of knowledge and existence but also explored the qualities of a good life and just society, contributing to the intellectual heritage that shapes contemporary discourse.</p>", "<p>The Roman Empire, known for its vast territorial expansion and cultural integration, offers a fascinating study of power and governance. At its height, the empire encompassed much of Europe, North Africa, and parts of Asia, which facilitated the exchange of ideas, goods, and cultures. The Romans excelled in engineering, constructing roads, aqueducts, and public buildings that not only showcased their architectural prowess but also helped unify the empire, enabling efficient trade and communication.</p><p>Moreover, Roman law and political philosophy laid essential groundwork for modern legal systems. The codification of laws addressed issues of justice and order within the expansive territory, influencing legal frameworks throughout history. The principles of Roman citizenship promoted a sense of belonging among diverse populations, allowing for a degree of cultural assimilation that has affected the trajectory of Western civilization. Understanding the intricate dynamics of the Roman Empire sheds light on the enduring influences that shaped modern society.</p>"]}	38	8
78	2	1	The Confluence of Ideology, Media, and Globalization in Modern Politics	RC	{"passages": ["<p>In recent years, the intersection of technology and politics has garnered significant attention. The emergence of digital platforms has transformed how political campaigns are conducted, with data analytics and targeted advertising playing pivotal roles in shaping voter behavior. Candidates now rely heavily on social media to build their brands, engage with constituents, and disseminate their messages, often bypassing traditional media outlets. This direct line of communication can galvanize support but also raises concerns about misinformation and the erosion of public trust.</p><p>The influence of technology is not confined to campaigning; it has lasting implications for governance and civic engagement. Governments increasingly employ digital tools to increase transparency and facilitate citizen participation in decision-making processes. However, the digital divide means that not all citizens have equal access to these resources, potentially exacerbating existing inequities. As political actors navigate this new terrain, they must address the challenges of ensuring that technology serves as a bridge rather than a barrier, fostering a more inclusive democratic process.</p>", "<p>The impact of globalization on national politics has become a topic of intense debate. Globalization refers to the increasing interconnectedness of economies, cultures, and populations across borders, and its effects are felt in varying degrees across different nations. For some, globalization has paved the way for economic growth and development, offering opportunities for trade and investment. Conversely, others argue that it has led to a loss of sovereignty and traditional ways of life, prompting a backlash against international institutions and agreements.</p><p>This tension is particularly evident in the context of immigration policy, where nations grapple with balancing the benefits of a diverse workforce against the fears of cultural dilution and economic competition. The rise of nationalist movements in various countries underscores a growing sentiment that globalization is undermining local interests. As political leaders contend with these challenges, they must navigate the delicate balance between embracing global collaboration and addressing the legitimate concerns of their constituencies.</p>", "<p>The role of ideology in shaping political landscapes cannot be overstated. Political ideologies, encompassing a spectrum from liberalism to conservatism, influence the policies and platforms of parties and candidates. In contemporary politics, many observers note a growing divergence between established parties and the grassroots movements that often emerge from public discontent. These movements frequently draw from a variety of ideological sources, reflecting a mélange of beliefs and values that don't align neatly with traditional party lines.</p><p>This ideological fragmentation poses challenges for political stability, as coalition-building becomes more complex in a landscape where multiple voices compete for attention. Moreover, the increasing polarization among voters complicates consensus-driven policymaking, often leading to gridlock in legislative bodies. As political actors seek to address pressing issues—such as climate change, healthcare, and economic inequality—they must navigate not only their respective ideologies but also the shifting sentiments of an electorate that is more informed and engaged than ever before.</p>", "<p>The relationship between media and politics is undergoing significant transformation in the digital age. Traditional media outlets, once the primary source of information for the public, now face competition from a plethora of online platforms that allow for the rapid dissemination of news and opinions. This shift has democratized information access, enabling citizens to engage with political content in unprecedented ways. However, it also raises critical questions regarding the reliability and accuracy of information consumed by the public.</p><p>The challenge of misinformation is profound, as false narratives can spread faster than factual reporting. Political leaders and institutions are tasked with combating this phenomenon, striving to restore credibility to information sources while harnessing the power of social media for positive engagement. As the public grapples with the implications of this new media landscape, it becomes increasingly vital for voters to develop critical media literacy skills to navigate the complexities of the information that shapes their understanding of political realities.</p>"]}	38	9
79	1	1	Analysis of Profit, Loss, and Discount Across Departments in Human Resources	PS	[{"data": {"HR": {"Loss_Amount": 10000, "Loss_Discount": 1000, "Profit_Amount": 30000, "Profit_Discount": 3000}, "IT": {"Loss_Amount": 8000, "Loss_Discount": 800, "Profit_Amount": 25000, "Profit_Discount": 2500}, "Sales": {"Loss_Amount": 5000, "Loss_Discount": 500, "Profit_Amount": 20000, "Profit_Discount": 2000}}, "type": "pivot table", "index": ["HR", "IT", "Sales"], "columns": ["Profit_Amount", "Loss_Amount", "Profit_Discount", "Loss_Discount"], "description": "This pivot table summarizes the profit and loss amounts along with their discounts across different departments."}]	41	9
80	1	1	Analysis of Sales and Profits Across Business Departments	PS	[{"data": {"Clothing": {"Q1 Sales": 15000, "Q2 Sales": 20000, "Q1 Profits": 3000, "Q2 Profits": 5000}, "Furniture": {"Q1 Sales": 30000, "Q2 Sales": 35000, "Q1 Profits": 10000, "Q2 Profits": 12000}, "Electronics": {"Q1 Sales": 20000, "Q2 Sales": 25000, "Q1 Profits": 5000, "Q2 Profits": 7000}}, "type": "pivot table", "index": ["Electronics", "Clothing", "Furniture"], "columns": ["Q1 Sales", "Q2 Sales", "Q1 Profits", "Q2 Profits"], "description": "This pivot table presents a comparison of sales and profits across different departments over two quarters."}]	41	10
81	1	1	Analysis of Logistics Operations: Expenses vs. Revenue in 2022	PS	[{"type": "bar graph", "graph": {"data": {"data": [8000, 10000, 12000, 15000, 18000, 12000, 16000, 20000, 22000, 25000, 23000, 24000], "x-axis": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], "y-axis": [0, 5000, 10000, 15000, 20000, 25000]}, "title": "Monthly Logistics Operations Expenses in 2022", "xAxis": "Months", "yAxis": "Expenses in USD"}, "description": "This bar graph illustrates the monthly logistics operations expenses throughout the year 2022."}, {"type": "bar graph", "graph": {"data": {"data": [10000, 15000, 18000, 22000, 26000, 22000, 27000, 30000, 32000, 34000, 33000, 35000], "x-axis": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], "y-axis": [0, 5000, 10000, 15000, 20000, 25000]}, "title": "Logistics Operations Revenue Trends in 2022", "xAxis": "Months", "yAxis": "Revenue in USD"}, "description": "This bar graph depicts the monthly revenue trends within logistics operations during 2022."}]	42	10
82	1	1	Analyzing Environmental Impact: A Data-Driven Approach to Sustainability and CO2 Emissions	PS	[{"rows": [[2015.0, 5000.0, 15.0, 0.75], [2016.0, 5200.0, 17.0, 0.76], [2017.0, 5400.0, 20.0, 0.77], [2018.0, 5600.0, 22.0, 0.78], [2019.0, 5800.0, 25.0, 0.79]], "type": "standard data table", "headers": ["Year", "CO2 Emissions (Million Metric Tons)", "Renewable Energy Usage (%)", "Biodiversity Index"], "description": "This standard data table illustrates the relationship between CO2 emissions, renewable energy usage, and biodiversity index over a span of five years."}, {"rows": [["Transportation", 1700, 10, 6], ["Industry", 2100, 12, 5], ["Residential", 800, 20, 7], ["Agriculture", 500, 15, 4], ["Commercial", 900, 18, 6]], "type": "standard data table", "headers": ["Sector", "CO2 Emissions (Million Metric Tons)", "Renewable Energy Usage (%)", "Sustainability Rating (1-10)"], "description": "This standard data table details the CO2 emissions, renewable energy usage, and sustainability ratings across various sectors."}]	42	11
83	1	1	Analyzing the Influence of Marketing Strategies on Sales Performance Using Scatter Plots	PS	null	42	12
84	2	1	Exploring the Dimensions of Psychological Study	RC	{"passages": ["<p>The field of psychology has long sought to understand the complex interplay between behavior and mental processes. Among the many theories that have emerged, cognitive psychology stands out for its focus on the internal processes by which individuals perceive, think, and remember. This branch of psychology emphasizes the importance of mental functions in understanding how people process information from their environments and make decisions based on that information.</p><p>One of the significant developments in cognitive psychology is the concept of cognitive distortions, which refers to the biased perspectives individuals may adopt about themselves and the world around them. This can lead to misinterpretations of reality, affecting emotional responses and behaviors. Understanding these distortions is critical for therapeutic practices, particularly in cognitive behavioral therapy (CBT), which aims to help individuals recognize and alter these maladaptive thought patterns.</p>", "<p>Another pivotal area of study within psychology is the realm of social psychology, which examines how an individual's thoughts, feelings, and behaviors are influenced by the actual, imagined, or implied presence of others. This field investigates a variety of phenomena, including conformity, group dynamics, and interpersonal relationships. Social psychologists explore questions such as why individuals often conform to group norms, even against their better judgment, and how social contexts can shape individual behavior.</p><p>Research in social psychology has also illuminated mechanisms behind prejudice and discrimination, revealing how stereotypes can influence perceptions and lead to biased behaviors. By understanding these social processes, psychologists aim to inform interventions that promote tolerance and reduce social conflict. In therapeutic settings, this knowledge can empower individuals to navigate their social worlds more effectively, fostering healthier relationships and reducing anxiety in social contexts.</p>", "<p>Developmental psychology represents yet another vital branch, focusing on the psychological growth and changes that occur throughout a person's lifespan. This field examines how various factors, such as genetics, environment, and social experiences, contribute to cognitive and emotional development. Key theories, like Erik Erikson's stages of psychosocial development, outline how individuals face different challenges and crises at various life stages, influencing their identity and personal growth.</p><p>Additionally, research in developmental psychology has highlighted the significance of early childhood experiences on later behavior and emotional health. Notably, attachment theory posits that the bonds formed with primary caregivers shape an individual's social and emotional capacities. Understanding these developmental processes is crucial for educators, parents, and mental health professionals alike, as it can guide interventions aimed at fostering healthy development and addressing developmental disorders.</p>"]}	43	7
85	2	1	The Duality of Knowledge: Exploration of Philosophical Thought	RC	{"passages": ["<p>The philosophical journey often commences with a sense of wonder, a curiosity about the nature of existence itself. Philosophers have pondered questions such as 'What is the meaning of life?' and 'Is there a reality beyond what we can perceive?' In exploring these inquiries, one may encounter various schools of thought, notably empiricism and rationalism. Empiricists argue that knowledge is derived from sensory experience, suggesting that our understanding of the world is fundamentally shaped by what we perceive through our senses. In contrast, rationalists contend that reason and innate ideas play a crucial role in the formation of knowledge, proposing that some truths can be known independently of sensory experience.</p><p>This dichotomy highlights the tension between two fundamentally different approaches to understanding truth. While empiricism emphasizes the role of experience and observation, rationalism elevates the power of intellect and reasoning. This ongoing debate has spurred countless discussions on the nature of knowledge and has influenced various disciplines, including science, ethics, and metaphysics, thereby illustrating the profound implications of these philosophical positions.</p>", "<p>Throughout history, philosophers have grappled with the concept of the self and its relation to the external world. The existentialist school of thought, championed by figures such as Jean-Paul Sartre and Simone de Beauvoir, posits that existence precedes essence; in other words, individuals are not born with a predetermined nature but instead create their identities through choices and actions. This belief in radical freedom underscores the weight of personal responsibility, urging individuals to forge their own paths in an indifferent universe.</p><p>Moreover, this philosophical viewpoint invites an exploration of authenticity and the struggle against societal norms that often dictate behavior. The existentialist perspective encourages one to confront the 'bad faith' that arises when individuals conform to external expectations at the expense of their true selves. Through such reflection, it becomes evident that understanding one's identity is not merely a philosophical exercise but an essential endeavor for leading a meaningful life amidst the complexities of existence.</p>", "<p>The concept of morality has been a focal point in philosophical discourse, with numerous theorists attempting to articulate the foundations of ethical behavior. Immanuel Kant's deontological ethics presents a framework in which moral actions are dictated by adherence to duty rather than the consequences of those actions. Kantian ethics asserts that one should act according to maxims that could be universally applied, thereby fostering a sense of moral obligation that transcends personal desires.</p><p>Conversely, utilitarianism, associated with philosophers such as Jeremy Bentham and John Stuart Mill, emphasizes the outcomes of actions, advocating for the greatest happiness principle. This perspective evaluates the morality of actions based on their ability to produce pleasure and minimize suffering for the greatest number of people. The tension between these two ethical paradigms invites critical reflection on the nature of morality and challenges individuals to consider whether ethical decisions should be based on duty or the pursuit of consequential benefits.</p>"]}	43	8
86	2	1	Photosynthesis and the Rise of Biotechnology	RC	{"passages": ["<p>The study of photosynthesis has captivated scientists for centuries. This process, whereby plants convert light energy into chemical energy, is fundamental to life on Earth. During photosynthesis, plants utilize sunlight to transform carbon dioxide and water into glucose and oxygen. These products serve as both an energy source for the plants themselves and a key component of the Earth's atmospheric balance.</p>", "<p>Recent advancements in biotechnology have led to the development of genetically modified organisms (GMOs). These innovations allow scientists to enhance crop resistance to pests and environmental conditions, potentially increasing food production. However, the introduction of GMOs has sparked significant debate regarding their safety and environmental impact, highlighting the need for ongoing research and regulation in this dynamic field.</p>"]}	44	7
87	2	1	The Shifts and Transformations of Historical Progress	RC	{"passages": ["<p>The study of history is often seen as a repository of factual events, but it is fundamentally an interpretation of the past. Historians seek to reconstrue narratives from the remnants of bygone eras, attempting to weave together disparate threads into cohesive stories. This effort requires not only a deep understanding of the events themselves but also an appreciation for the context in which these events occurred. For instance, the fall of the Roman Empire is not merely recorded in terms of battles lost or territories gained, but understood through the lens of shifting cultural, social, and economic factors that precipitated its decline.</p><p>Moreover, the interpretation of history is inherently subjective; different historians may emphasize various elements of the same event based on their perspectives and the contemporary issues they wish to address. The evolution of historical narratives over time reveals much about the societies that produced them. The tumultuous history of colonization, for example, has been portrayed in radically diverse ways, reflecting ongoing conversations about power, race, and identity. As such, history is not a static record, but a dynamic field that evolves with new research and societal shifts.</p>", "<p>The Renaissance period marks a significant turning point in European history, characterized by a revival of interest in the classical art and philosophies of ancient Greece and Rome. This cultural movement, which spanned from the 14th to the 17th centuries, fostered a spirit of inquiry and innovation that profoundly impacted art, science, and politics. Artists such as Leonardo da Vinci and Michelangelo redefined artistic boundaries, employing techniques such as chiaroscuro and perspective to create lifelike representations of the human form. Their works, steeped in humanism, illustrated not only a mastery of technique but also a new appreciation for individual experience and emotion.</p><p>Simultaneously, scientific advancements began to flourish, as thinkers like Copernicus and Galileo challenged established notions of the cosmos, proposing revolutionary ideas that would lay the groundwork for modern science. This intellectual ferment was further nurtured by the invention of the printing press, which facilitated the widespread dissemination of ideas and allowed for the questioning of authority. The Renaissance exemplifies a period where the confluence of artistry and science fostered a profound transformation in European thought, encouraging a forward-looking exploration that would define the subsequent eras.</p>", "<p>The Industrial Revolution, spanning from the late 18th to the mid-19th century, was a period of profound change that transformed societies around the globe. Beginning in Great Britain, it marked the transition from agrarian economies to industrialized and urban ones. The introduction of machinery and factory production fundamentally altered the nature of labor; artisans and craftsmen were increasingly replaced by factory workers, leading to a new social order characterized by the rise of the working class. This shift contributed to significant demographic changes, as people moved to urban centers in search of employment opportunities.</p><p>However, the Industrial Revolution was not merely an economic transformation; it brought with it a plethora of social and environmental consequences. While it spurred unprecedented wealth and advancements in technology, it also gave rise to brutal working conditions, child labor, and environmental degradation. Reactions to these challenges spurred movements advocating for labor rights and social reforms, indicating that the progress achieved was often accompanied by significant social strife. Thus, the Industrial Revolution serves as a complex chapter in history, illustrating the duality of progress and the accompanying challenges it often entails.</p>"]}	44	8
88	2	1	The Dynamics of Economics: Balancing Choices and Consequences	RC	{"passages": ["<p>The concept of economics is fundamentally concerned with how societies allocate scarce resources. In an increasingly interconnected world, the principles of economics help to explain how individuals and institutions make choices regarding production, distribution, and consumption. For instance, when a government decides to fund public education, it is effectively reallocating resources that could have been used in other sectors of the economy. This decision illustrates the trade-offs inherent in economic decision-making.</p><p>Furthermore, economic theories offer insights into the behavior of markets. Supply and demand, a foundational principle of economics, posits that prices are determined by the availability of goods and the desire of consumers to purchase them. When demand exceeds supply, prices tend to rise, prompting producers to increase production, thus eventually achieving a market equilibrium. An understanding of these concepts is essential for both policymakers and businesses alike, as it influences their strategic decisions.</p>", "<p>Economics is often divided into two main branches: microeconomics and macroeconomics. Microeconomics focuses on the individual and firm-level decisions, analyzing how consumers respond to changes in prices and how firms determine their production levels. For example, when the price of a popular consumer good increases, microeconomic principles suggest that consumers may either seek substitutes or reduce their overall consumption, thereby influencing market dynamics.</p><p>On the other hand, macroeconomics examines the economy as a whole, investigating factors like national income, overall employment, and inflation rates. Policymakers utilize macroeconomic indicators to assess economic health and develop strategies to promote growth. Understanding the cyclical nature of economies, including periods of expansion and recession, is crucial for crafting effective economic policies. The interplay between micro and macroeconomic factors highlights the complexity of economic systems and the challenges faced by decision-makers.</p>", "<p>One vital concept in economics is that of opportunity cost, which refers to the value of the next best alternative forgone when a choice is made. For example, if a student chooses to attend college instead of working full-time, the opportunity cost includes not just the lost wages but also the experience and skills that could have been gained through employment. This concept is essential for both individuals and businesses to understand, as it shapes their decision-making processes regarding resource allocation.</p><p>Additionally, the role of incentives in economics cannot be overstated. Incentives can motivate behavior and influence individuals and organizations to act in certain ways. For instance, tax reductions can incentivize investment in businesses, leading to job creation and economic growth. Conversely, disincentives, such as taxes on sugary drinks, are designed to reduce consumption of unhealthy products. Recognizing the power of incentives is crucial for the effective formulation of both economic policies and business strategies.</p>", "<p>Globalization is a defining feature of the modern economy, characterized by the increasing interdependence of countries worldwide. Through trade, investment, and technology transfer, globalization enhances economic growth and offers consumers a wider choice of goods and services. However, it also presents challenges, such as job displacement in certain sectors and income inequality within countries. Understanding the implications of globalization is critical for governments as they pursue policies that can maximize its benefits while mitigating its adverse effects.</p><p>Moreover, the phenomenon of economic development concerns the improvements in living standards and the quality of life in a nation. Economic development takes into account not just the growth of GDP but also factors like education, healthcare, and environmental sustainability. Policymakers aim to foster economic development by implementing strategies that promote innovation, infrastructure investment, and fair trade practices. Balancing the various aspects of economic development is crucial for ensuring long-term prosperity and equity among citizens.</p>"]}	44	9
89	1	1	Analyzing Sales Performance Across Various Marketing Channels and Product Categories	PS	[{"data": {"Online": {"Q1": 15000, "Q2": 20000, "Q3": 25000, "Q4": 30000}, "Retail": {"Q1": 10000, "Q2": 15000, "Q3": 20000, "Q4": 25000}, "Wholesale": {"Q1": 5000, "Q2": 7000, "Q3": 8000, "Q4": 9000}}, "type": "pivot table", "index": ["Marketing Channel", "Sales Quarter"], "columns": ["Q1", "Q2", "Q3", "Q4"], "description": "This pivot table summarizes the sales data across different marketing channels and quarters. It compares the revenue generated through Online, Retail, and Wholesale channels in each quarter."}, {"data": {"Clothing": {"Q1": 15000, "Q2": 20000, "Q3": 25000, "Q4": 30000}, "Furniture": {"Q1": 8000, "Q2": 9000, "Q3": 10000, "Q4": 11000}, "Electronics": {"Q1": 20000, "Q2": 30000, "Q3": 40000, "Q4": 50000}}, "type": "pivot table", "index": ["Product Category", "Sales Quarter"], "columns": ["Q1", "Q2", "Q3", "Q4"], "description": "This pivot table illustrates the sales figures for different product categories across four quarters, highlighting the sales performance of Electronics, Clothing, and Furniture."}]	47	8
90	1	1	Analyzing the Impact of Government Policies on Compliance Rates Through Scatter Plot	PS	null	47	9
91	1	1	Analyzing Profit, Loss, and Discount Rates in Sustainable Product Management	PS	[{"data": {"Product A": {"Loss": 5000, "Profit": 20000, "Discount": 3}, "Product B": {"Loss": 3000, "Profit": 15000, "Discount": 5}, "Product C": {"Loss": 2000, "Profit": 18000, "Discount": 6}}, "type": "pivot table", "index": ["Year", "Product"], "columns": ["Profit", "Loss", "Discount"], "description": "This pivot table illustrates the annual profit, loss, and discount rates for various products over three years, showcasing their financial performance."}, {"data": {"Product A": {"Loss": 7000, "Profit": 25000, "Discount": 4}, "Product B": {"Loss": 4000, "Profit": 17000, "Discount": 5}, "Product C": {"Loss": 2500, "Profit": 20000, "Discount": 7}}, "type": "pivot table", "index": ["Year", "Product"], "columns": ["Profit", "Loss", "Discount"], "description": "This pivot table represents the financial data for different products indicating changes in profit, loss, and discount rates over a specific timeframe, helping analyze their performance."}]	48	9
92	1	1	Analysis of Financial Performance: Revenue vs Expenses from 2010 to 2020	PS	[{"type": "line graph", "graph": {"data": {"data": [50, 150, 300, 400, 500, 600, 700, 800, 900, 950, 1000], "x-axis": [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020], "y-axis": [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]}, "title": "Annual Revenue Growth from 2010 to 2020", "xAxis": "Years", "yAxis": "Revenue (in millions)"}, "description": "This line graph illustrates the annual revenue growth of a hypothetical company from 2010 to 2020, showcasing the company's increasing financial success over the decade."}, {"type": "line graph", "graph": {"data": {"data": [30, 80, 150, 300, 350, 450, 500, 550, 600, 650, 700], "x-axis": [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020], "y-axis": [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]}, "title": "Annual Expense Growth from 2010 to 2020", "xAxis": "Years", "yAxis": "Expenses (in millions)"}, "description": "This line graph illustrates the annual expense growth of a hypothetical company from 2010 to 2020, showing an increase in operational costs over the same period."}]	48	10
93	1	1	Analyzing the Impact of Artificial Intelligence Across Industries	PS	[{"type": "pie chart", "graph": {"data": [{"name": "Healthcare", "color": "#0405ef", "value": 25}, {"name": "Finance", "color": "#ef0523", "value": 35}, {"name": "Retail", "color": "#05ef04", "value": 20}, {"name": "Manufacturing", "color": "#ef0523", "value": 10}, {"name": "Transportation", "color": "#ef0512", "value": 10}], "title": "Distribution of AI Applications in Various Industries"}, "description": "This pie chart illustrates the distribution of artificial intelligence applications across different industries, indicating the prevalence of AI technologies in sectors like healthcare, finance, retail, manufacturing, and transportation."}, {"type": "line graph", "graph": {"data": {"data": [50, 75, 120, 180, 250, 320, 400, 500, 600, 650, 700], "x-axis": [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025], "y-axis": [0, 50, 100, 150, 200, 250, 300, 400, 500, 600, 700]}, "title": "Growth of AI Market Value from 2015 to 2025", "xAxis": "Year", "yAxis": "Market Value in Billion USD"}, "description": "This line graph displays the projected growth of the artificial intelligence market value from 2015 to 2025, showing an upward trend in market value across the years."}]	48	11
94	2	1	Exploring the Intricacies of Atmospheric Pressure, Genetic Engineering, and Quantum Entanglement	RC	{"passages": ["<p>The intricate relationship between atmospheric pressure and weather patterns has long captivated scientists and meteorologists alike. Atmospheric pressure, the weight of air pressing down on the Earth's surface, significantly influences climatic variations across different regions. Notably, areas of high pressure, usually associated with descending air, tend to produce clear, sunny conditions, whereas low-pressure zones are characterized by rising air that often leads to cloud formation and precipitation.</p><p>This interplay becomes particularly evident in the context of cyclones and anticyclones. Cyclones, or areas of low pressure, draw air inwards and upwards, facilitating the development of storm systems. Conversely, anticyclones, or high-pressure systems, promote stability in the atmosphere, suppressing storm development. Understanding the mechanisms underlying these systems is critical for predicting weather changes and preparing for extreme weather events, which are becoming increasingly prevalent in a changing climate.</p>", "<p>The advancement of genetic engineering has opened new horizons in the field of biotechnology, allowing scientists to manipulate the genetic material of organisms with unprecedented precision. At the heart of this revolution lies CRISPR-Cas9 technology, which enables targeted modifications to DNA sequences. This method has been employed to engineer crops that are resistant to pests and diseases, enhancing food security in the face of a burgeoning global population.</p><p>Moreover, the implications of genetic engineering extend beyond agriculture. In medical research, techniques derived from CRISPR have facilitated the development of gene therapies aimed at treating hereditary diseases, transforming the landscape of potential treatments. However, the rapid pace of advancements has also sparked ethical debates surrounding genetic modification, particularly concerning its application in humans. These discussions emphasize the need for regulations to ensure responsible research and the equitable distribution of its benefits.</p>", "<p>The phenomenon of quantum entanglement has solidified its relevance within the realm of modern physics, challenging our classical intuitions about the nature of reality. Entanglement refers to a quantum state wherein particles become interlinked, such that the state of one particle instantaneously influences the state of another, regardless of the distance separating them. This observation, famously dubbed 'spooky action at a distance' by Albert Einstein, has been substantiated through numerous experiments, leading to profound implications for the fields of quantum computing and cryptography.</p><p>Furthermore, entanglement raises intriguing philosophical questions pertaining to locality and determinism. It compels scientists and philosophers alike to reconsider the foundational principles of physics, including causality and time. As research continues to unveil the complexities of these quantum systems, the challenge lies not only in harnessing their potential for technological advancement but also in grappling with the theoretical ramifications of a world governed by quantum mechanics.</p>"]}	49	6
95	2	1	The Interplay of Policy and Economic Dynamics	RC	{"passages": ["<p>The study of economics as a discipline encompasses not only the examination of financial transactions and markets but also extends to the intricate interplay between human behavior and resource allocation. At its core, economics seeks to elucidate how individuals and societies make choices in the face of scarcity, with the fundamental premise that resources are limited while human wants are virtually boundless. This duality creates a series of trade-offs that are crucial for understanding both micro and macroeconomic principles.</p><p>In recent years, the field has witnessed a paradigm shift towards behavioral economics, which synthesizes insights from psychology with traditional economic models. This evolving perspective acknowledges that human decision-making deviates from the rational actor model, influenced by cognitive biases and emotional responses. As a result, policymakers are increasingly incorporating behavioral insights to design interventions that nudge individuals towards more beneficial economic behaviors, such as saving for retirement or reducing energy consumption. The implications of these approaches extend beyond mere financial indicators, affecting the overall welfare of societies and challenging the conventional wisdom of economic theory.</p>", "<p>The global economy has become increasingly interdependent in the 21st century, highlighting the necessity for comprehensive trade policies that reflect the complexities of globalization. As countries engage in international trade, they must navigate both the benefits and the challenges posed by this interconnectedness. Trade agreements, while designed to lower tariffs and enhance market access, often lead to contentious debates regarding their impact on domestic industries and employment levels. Industries that are exposed to foreign competition frequently lobby for protective measures, underscoring the tensions between free trade principles and national economic interests.</p><p>Furthermore, the advent of digital technology has revolutionized trade practices, enabling e-commerce and the rapid exchange of information across borders. As digital platforms flourish, they reshape consumer expectations and business models, presenting new opportunities for growth. However, this transformation also raises concerns about regulatory challenges, data privacy, and the digital divide that may exacerbate inequalities between developed and developing nations. Policymakers thus face the difficult task of balancing the promotion of innovative economic practices with the need to safeguard public interests.</p>", "<p>Monetary policy plays a pivotal role in shaping economic stability and growth, particularly through the actions of central banks. Throughout history, various monetary frameworks have evolved, each reflecting differing philosophies about the role of money supply and interest rates. The transition from the gold standard to fiat currency systems, for example, marked a significant shift in how monetary authorities operate. Central banks now wield substantial influence, utilizing tools such as open market operations and interest rate adjustments to manage inflation and stimulate employment. However, the effectiveness of these policies often comes under scrutiny, especially during periods of economic volatility.</p><p>In recent years, unconventional monetary policies, such as quantitative easing, have gained prominence as traditional methods reach their limits. Central banks have resorted to purchasing large quantities of government securities to inject liquidity into the economy, aiming to encourage lending and investment. While proponents argue that such measures are essential for recovery during economic downturns, critics raise concerns about long-term implications, including asset bubbles and income inequality. This debate underscores the necessity of a nuanced understanding of monetary policy's effects and the broader economic landscape.</p>", "<p>The relationship between fiscal policy and economic performance is a complex and often contested area within the field of economics. Fiscal policy, which encompasses government spending and taxation, serves as a crucial counterbalance to the forces of the market. Economists debate the efficacy of various fiscal strategies, particularly in the context of stimulating growth during economic recessions. Keynesian economics advocates for increased government spending to stimulate demand, while supply-side economics emphasizes tax cuts as a means to enhance economic productivity. The effectiveness of these contrasting approaches often hinges on the particular economic conditions faced by a country.</p><p>Moreover, the increasing public debt levels in many countries have sparked significant discussions around sustainability and fiscal responsibility. As governments respond to economic crises with robust stimulus packages, concerns regarding long-term fiscal health inevitably arise. Critics warn that excessive borrowing could lead to higher interest rates, crowding out private investment, whereas supporters assert that strategic debt financing can facilitate robust economic recovery. Ultimately, the challenge lies in balancing immediate economic needs with long-term fiscal stability, necessitating a careful and informed approach to fiscal policymaking.</p>"]}	49	7
96	2	1	Exploring the Depths of Philosophical Inquiry	RC	{"passages": ["<p>Philosophy, at its core, investigates the fundamental nature of existence, knowledge, and values. It challenges individuals to question their beliefs and to rationalize the principles that govern their understanding of life. In this quest for meaning, philosophers engage in rigorous discourse, often dissecting concepts such as morality, reality, and the human condition. The interplay between subjective experiences and objective truths forms the crux of many philosophical debates, prompting individuals to reflect deeply on their own perspectives.</p><p>As philosophy evolves, it increasingly intersects with other disciplines, including science, psychology, and social theory. This interdisciplinarity enriches philosophical inquiry, allowing for a more nuanced understanding of complex issues. Notably, contemporary philosophers advocate for the applicability of philosophical reasoning to real-world dilemmas, asserting that theoretical discussions must inform practical actions.</p>", "<p>The concept of free will is a perennial topic in philosophy, one that evokes profound contemplation about human agency and determinism. Philosophers debate whether humans possess the ability to choose actions independently or whether their decisions are predetermined by external factors such as genetics, culture, or environment. This inquiry poses significant implications for moral responsibility; if free will is an illusion, the very foundation of ethics might be called into question.</p><p>Recent developments in neuroscience have provided insights that complicate traditional views on free will. Studies suggest that brain activity related to decision-making may occur before individuals become consciously aware of their choices. Such findings invite further exploration of the nuances of autonomy and the extent to which individuals can claim ownership of their actions. As this dialogue continues, it challenges fundamental assumptions about individuality and ethical accountability.</p>"]}	50	7
97	2	1	Transformative Epochs: The Renaissance, Industrial Revolution, and American Revolution	RC	{"passages": ["<p>The Renaissance, a cultural movement that began in Italy during the 14th century, marked a significant turning point in European history. It is characterized by a revival of classical learning and wisdom, leading to remarkable advancements in art, literature, and science. Artists like Leonardo da Vinci and Michelangelo embraced humanism, which emphasized human potential and achievement. This period not only saw the flourishing of art but also the emergence of new ideas about politics and society, setting the stage for the modern world.</p><p>Moreover, the invention of the printing press in the 15th century significantly contributed to the spread of knowledge. Books became more accessible to the general public, facilitating the exchange of ideas and promoting literacy. The Renaissance's focus on individualism and inquiry paved the way for the Reformation and the Age of Enlightenment, ultimately transforming European society and thought.</p>", "<p>The Industrial Revolution, which began in the late 18th century in Britain, was a period of great technological advancement and economic change. It marked the transition from hand production methods to machines, leading to the establishment of factories. This period saw inventions such as the steam engine, which revolutionized transportation and industry. As a result, goods could be produced more efficiently, and as production increased, so did the demand for labor.</p><p>With the rise of factories, urbanization became a key feature of this era. People moved from rural areas to cities in search of work, leading to significant demographic changes. Although the Industrial Revolution spurred economic growth and improved living standards for some, it also brought challenges, including labor exploitation and environmental degradation. The implications of this transformation continue to influence modern society, as the patterns of industrialization shaped contemporary economic and social structures.</p>", "<p>The American Revolution, occurring between 1775 and 1783, was a pivotal event in world history. It stemmed from growing tensions between the American colonies and British authorities over issues such as taxation without representation and the desire for self-governance. The conflict ultimately led to the colonies' quest for independence, which was famously articulated in the Declaration of Independence in 1776.</p><p>The revolution not only resulted in the establishment of the United States of America but also inspired other nations to pursue their own quests for liberty and democratic governance. The principles of equality and individual rights advocated during this time became foundational to modern democratic ideologies. Additionally, the success of the American Revolution set a precedent for future revolutionary movements, illustrating the power of collective will in the face of oppression.</p>"]}	50	8
98	2	1	Exploring the Essence of Scientific Inquiry and Its Impact	RC	{"passages": ["<p>The field of science has always been a domain of inquiry and exploration, uncovering the mechanisms that govern the natural world. From the smallest particle to the vastness of the cosmos, scientific endeavors seek to describe and explain phenomena through observation, experimentation, and reasoning. The scientific method is not just a systematic approach but a philosophy that encourages skepticism and critical thinking, enabling scientists to challenge existing paradigms and expand the boundaries of knowledge.</p><p>One of the most significant principles in science is falsifiability; a hypothesis must be testable and falsifiable to hold scientific merit. This tenet distinguishes scientific inquiry from belief-based systems, allowing for the rejection of theories in the face of contrary evidence. Over centuries, the scientific community has been responsible for numerous breakthroughs, from the understanding of gravity to the discoveries of DNA's structure, demonstrating how systematic investigation leads to profound advancements in technology and medicine.</p>", "<p>Scientific discovery often requires a collaborative approach, where researchers from various disciplines come together to tackle complex challenges. Such interdisciplinary efforts can lead to innovative solutions that would be unattainable within the confines of a single field. For instance, the merging of biology and engineering has given rise to fields like biotechnology, where biological processes are harnessed to create products beneficial to humanity.</p><p>Moreover, the advancement of technology has greatly impacted scientific research, providing tools that enhance data collection and analysis. Modern instruments such as electron microscopes and particle accelerators have expanded our ability to explore the universe at unprecedented levels of detail. As science progresses, it continues to raise ethical questions regarding its applications, making it essential for scientists to consider the implications of their work on society and the environment.</p>", "<p>Another vital aspect of science is the role of peer review, a process that subjects research findings to the scrutiny of fellow scientists before publication. This mechanism ensures that the research meets the rigorous standards of validity and reliability, fostering a culture of accountability within the scientific community. Peer review not only helps to maintain quality but also serves as a vital tool for knowledge dissemination, making sure that accurate information reaches the wider public and informs future research.</p><p>Furthermore, science education plays a crucial role in inspiring the next generation of scientists. By fostering curiosity and critical thinking from a young age, educational initiatives aim to cultivate a populace that values empirical evidence and rational discourse. As the global challenges we face become increasingly complex, a scientifically literate society is essential for informed decision-making and problem-solving.</p>", "<p>The public's perception of science is shaped by various factors, including media representation and cultural beliefs. Misinformation can spread rapidly, often leading to skepticism about scientific findings. To counteract this, scientists and educators must strive to communicate their discoveries effectively, emphasizing transparency and accessibility. Engaging the public through outreach programs, social media, and community workshops can foster a better understanding of scientific principles.</p><p>Ultimately, science is a vital endeavor that transcends boundaries, contributing to advancements in health, technology, and environmental sustainability. As we move forward, it is imperative to support scientific research and its applications, while also fostering a dialogue that encourages critical examination and ethical considerations of scientific practices.</p>"]}	50	9
\.


--
-- Data for Name: _prisma_migrations; Type: TABLE DATA; Schema: public; Owner: compexe_admin
--

COPY public._prisma_migrations (id, checksum, finished_at, migration_name, logs, rolled_back_at, started_at, applied_steps_count) FROM stdin;
0469c84b-530e-4566-ac85-65a4851ecc56	883e9d87a91431b898bb5d167bafa36af14f935cf2415325fdce5bb85b991fb1	2025-02-06 18:43:14.538879+00	20250206184314_enabling_mock_component	\N	\N	2025-02-06 18:43:14.505804+00	1
646626e3-9831-4ee0-832e-4090b49c997a	3c979ee3040b7c4bcf4dcc97042d09a3493f5797c1e539c0949a23e960f265d2	2025-02-07 02:31:07.458631+00	20250207023107_fixed_mockquestionnumber_spelling_in_problems_table	\N	\N	2025-02-07 02:31:07.456059+00	1
\.


--
-- Data for Name: examtypes; Type: TABLE DATA; Schema: public; Owner: compexe_admin
--

COPY public.examtypes (examtypeid, name, description) FROM stdin;
1	GRE	Graduate Record Examination
2	GMAT	Graduate Management Admission Test
\.


--
-- Data for Name: mocksections; Type: TABLE DATA; Schema: public; Owner: compexe_admin
--

COPY public.mocksections (mocksectionid, mocktestid, sectionnumber, sectionid) FROM stdin;
32	20	0	3
33	20	0	4
34	20	0	5
35	21	1	1
36	21	2	1
37	21	1	2
38	21	2	2
39	22	0	3
40	22	0	4
41	23	1	1
42	23	2	1
43	23	1	2
44	23	2	2
45	24	0	3
46	24	0	4
47	25	1	1
48	25	2	1
49	25	1	2
50	25	2	2
\.


--
-- Data for Name: mocktestrankings; Type: TABLE DATA; Schema: public; Owner: compexe_admin
--

COPY public.mocktestrankings (rankingid, userid, mocktestid, rank, percentile) FROM stdin;
\.


--
-- Data for Name: mocktests; Type: TABLE DATA; Schema: public; Owner: compexe_admin
--

COPY public.mocktests (mocktestid, difficulty, examtypeid, date, starttime, endtime, isactive) FROM stdin;
20	1	2	2025-02-07	10:51:30.265	10:51:30.265	t
21	1	1	2025-02-08	09:58:31.963	09:58:31.963	t
22	2	2	2025-02-08	10:37:53.451	10:37:53.451	t
23	2	1	2025-02-08	10:41:41.994	10:41:41.994	t
24	3	2	2025-02-09	03:33:00.797	03:33:00.797	t
25	3	1	2025-02-09	03:43:40.09	03:43:40.09	t
\.


--
-- Data for Name: mocktestsectionscores; Type: TABLE DATA; Schema: public; Owner: compexe_admin
--

COPY public.mocktestsectionscores (scoreid, attemptid, sectionid, score) FROM stdin;
\.


--
-- Data for Name: performance; Type: TABLE DATA; Schema: public; Owner: compexe_admin
--

COPY public.performance (userid, sectionid, correctcount, incorrectcount, partialcorrectcount, averagespeed) FROM stdin;
\.


--
-- Data for Name: problemoptions; Type: TABLE DATA; Schema: public; Owner: compexe_admin
--

COPY public.problemoptions (optionid, problemid, optiontext, iscorrect, "group") FROM stdin;
2292	541	20	t	\N
2293	541	10	f	\N
2294	541	10	f	\N
2295	541	25	f	\N
2296	542	10.0\\$	f	\N
2297	542	8.0\\$	f	\N
2298	542	12.0\\$	t	\N
2299	542	15.0\\$	f	\N
2300	543	63.8	f	\N
2301	543	64.68	f	\N
2302	543	53.8	f	\N
2303	543	58.8	t	\N
2304	543	52.92	f	\N
2305	544	11	f	\N
2306	544	8	f	\N
2307	544	10	f	\N
2308	544	9	t	\N
2309	546	9.4x	f	\N
2310	546	4.7x	t	\N
2311	546	4.6x	f	\N
2312	546	5.7x	f	\N
2313	547	x >= 1500, y >= 1200, x + y <= 3000	t	\N
2314	547	x >= 1500, y <= 1200, x + y <= 3000	f	\N
2315	547	x >= 1500, y >= 1200, x + y >= 3000	f	\N
2316	547	x < 1500, y >= 1200, x + y <= 3000	f	\N
2317	547	x >= 1300, y >= 1200, x + y <= 3000	f	\N
2318	548	4	f	\N
2319	548	6	f	\N
2320	548	2	f	\N
2321	548	5	t	\N
2322	549	17.5	f	\N
2323	549	26.76	f	\N
2324	549	25.4	t	\N
2325	549	13.77	f	\N
2326	550	6.0 kg	t	\N
2327	550	5.0 kg	f	\N
2328	550	8.0 kg	f	\N
2329	550	3.0 kg	f	\N
2330	550	9.0 kg	f	\N
2331	551	6	f	\N
2332	551	6	f	\N
2333	551	8	t	\N
2334	551	10	f	\N
2335	551	7	f	\N
2336	552	32	t	\N
2337	552	22	f	\N
2338	552	35	f	\N
2339	552	37	f	\N
2340	553	1200.00	t	\N
2341	553	1200.00	t	\N
2342	553	1600.00	f	\N
2343	553	945.00	f	\N
2344	554	120.0 pounds	f	\N
2345	554	250.0 pounds	f	\N
2346	554	200.0 pounds	f	\N
2347	554	150.0 pounds	t	\N
2348	555	140 km/h	f	\N
2349	555	150 km/h	f	\N
2350	555	130 km/h	f	\N
2351	555	135 km/h	t	\N
2352	556	8.68 hours	f	\N
2353	556	9.18 hours	f	\N
2354	556	9.81 hours	f	\N
2355	556	9.09 hours	t	\N
2356	557	\\$1500	f	\N
2357	557	\\$1500	f	\N
2358	557	\\$1450	t	\N
2359	557	\\$1350	f	\N
2360	558	2.67 kg	t	\N
2361	558	2.33 kg	f	\N
2362	558	1.83 kg	f	\N
2363	558	3.67 kg	f	\N
2364	559	40.0	t	\N
2365	559	50.0	f	\N
2366	559	30.0	f	\N
2367	559	30.0	f	\N
2368	560	90	f	\N
2369	560	104	f	\N
2370	560	96	f	\N
2371	560	100	t	\N
2372	561	37	f	\N
2373	561	30	f	\N
2374	561	32	t	\N
2375	561	42	f	\N
2376	561	29	f	\N
2377	562	15x + 25y >= 3000 and x + y >= 200	f	\N
2378	562	15x + 25y > 3000 and x + y < 200	f	\N
2379	562	15x + 20y >= 3000 and x + y <= 200	f	\N
2380	562	15x + 25y >= 3000 and x + y <= 200	t	\N
2381	563	$2572.81	f	\N
2382	563	$2422.81	f	\N
2383	563	$2522.81	t	\N
2384	563	$2322.81	f	\N
2385	564	Societal norms are increasingly ignoring utilitarian principles.	f	\N
2386	564	Utilitarianism has no significant influence on public policy.	f	\N
2387	564	Utilitarian principles likely contribute to a more collective approach in ethical decision-making.	t	\N
2388	564	Individual rights are prioritized over the well-being of the majority in utilitarian ethics.	f	\N
2389	564	Utilitarianism has been completely rejected in modern ethical discussions.	f	\N
2390	565	Physical activity can also lead to injuries if not managed properly.	f	\N
2391	565	Most students prefer sedentary activities over physical exercise.	f	\N
2392	565	Research shows that students who engage in physical activity have lower stress levels.	t	\N
2393	565	Increased physical activity leads to higher academic performance among students.	f	\N
2394	565	Many students are unable to participate in sports due to various barriers.	f	\N
2395	566	Social media is leading to more face-to-face interactions among teenagers.	f	\N
2396	566	Traditional media sources are gaining popularity among the youth.	f	\N
2397	566	Teenagers prefer obtaining information from books rather than online sources.	f	\N
2398	566	Teenagers are increasingly sharing experiences online over traditional communication methods.	t	\N
2399	566	Social media has no significant effect on the way teenagers connect with each other.	f	\N
2400	567	The findings support the idea that using libraries correlates with increased civic participation.	t	\N
2401	567	Access to public libraries has no relationship with community voting rates.	f	\N
2402	567	Public libraries are essential for fostering civic engagement among residents.	f	\N
2403	567	Only well-resourced libraries contribute to democratic processes in their communities.	f	\N
2404	567	Individuals who use public libraries are more likely to have higher levels of education.	f	\N
2405	568	The debate on moral relativism is irrelevant to contemporary ethical considerations.	f	\N
2406	568	Critics of moral relativism argue for the necessity of universal moral standards to prevent harm.	t	\N
2407	568	Moral relativism suggests that all moral frameworks are equally valid regardless of their principles.	f	\N
2408	568	Moral relativism supports the idea that ethical practices can remain unchanged over time.	f	\N
2409	568	Proponents of moral relativism believe that only one cultural perspective should dominate moral discussions.	f	\N
2410	569	Ethical decisions are best made by considering the greatest good for the greatest number.	f	\N
2411	569	All moral actions must prioritize individual happiness over collective well-being.	f	\N
2412	569	Moral rights and duties are always determined by the consequences of actions.	f	\N
2413	569	Consequentialist theories provide a stronger framework for moral decision-making.	f	\N
2414	569	There are actions that are inherently right or wrong regardless of outcomes.	t	\N
2415	570	Individuals can only maintain their cultural identity by completely rejecting outside influences.	f	\N
2416	570	Cultural practices evolve in response to external influences while still being embraced by individuals.	t	\N
2417	570	Cultural identity is solely based on rigid traditions that remain unchanged over time.	f	\N
2418	570	The transformation of culture is a recent phenomenon that has no historical precedent.	f	\N
2419	570	Cultural identity is only valuable when it remains static and unchanging.	f	\N
2420	571	initiated a new era of artistic expression and scientific exploration.	t	\N
2421	571	had minimal effects on the development of modern society.	f	\N
2422	571	led to a decline in philosophical thought and innovation.	f	\N
2423	571	restricted the progress of technology and science.	f	\N
2424	571	was solely focused on returning to ancient Greek art styles.	f	\N
2425	572	Prior to the printing press, handwritten manuscripts were limited to a small audience, limiting the spread of knowledge.	f	\N
2426	572	Many artists during the Renaissance were inspired by classical texts that were made widely available through printed materials.	t	\N
2427	572	The economic prosperity of cities during the Renaissance allowed for greater investment in literature and education.	f	\N
2428	572	The Renaissance was marked by a decline in religious influence, leading to a new focus on secular ideas.	f	\N
2429	572	The printing press was used exclusively for religious texts, contributing little to secular knowledge.	f	\N
2430	573	These scientific principles are essential for the development of innovative technologies, such as renewable energy and quantum computing.	t	\N
2431	573	Scientific advances in physics are solely confined to theoretical frameworks and do not translate into practical applications.	f	\N
2432	573	Understanding these concepts is primarily important for academic purposes and does not influence real-world technology.	f	\N
2433	573	The principles of physical sciences have no significant impact on contemporary technological applications.	f	\N
2434	574	The principles of quantum mechanics are confirmed by classical physics, providing no significant change in our understanding of reality.	f	\N
2435	574	The theories in quantum mechanics support the idea that reality operates solely on deterministic principles.	f	\N
2436	574	Quantum mechanics leads to practical benefits only, without affecting theoretical frameworks.	f	\N
2437	574	Quantum mechanics fundamentally alters our perception of reality by introducing concepts such as wave-particle duality and entanglement.	t	\N
2438	575	Maxwell's equations emphasize that electric currents cannot generate magnetic fields.	f	\N
2439	575	Maxwell's equations provide an argument that electricity and magnetism are completely independent phenomena.	f	\N
2440	575	Maxwell's equations describe how electric charges create electric fields.	t	\N
2441	575	Maxwell's equations state that electric fields do not influence magnetic fields.	f	\N
2442	576	The argument asserts that physical sciences operate independently of each other, thus emphasizing the uniqueness of each field.	f	\N
2443	576	The argument emphasizes that all physical phenomena are governed by strict deterministic laws, limiting the scope of scientific inquiry.	f	\N
2444	576	The argument highlights how advancements in one scientific field can lead to breakthroughs in others, demonstrating their mutual reliance.	t	\N
2445	576	The argument suggests that the complexities of climate change can be resolved through singular scientific approaches, reinforcing a limited perspective.	f	\N
2446	577	Single-discipline studies are deemed sufficient to tackle environmental issues on their own.	f	\N
2447	577	Interdisciplinary research is primarily motivated by funding opportunities rather than a genuine interest in scientific collaboration.	f	\N
2448	577	Interdisciplinary research is considered less important than traditional approaches focused solely on physical sciences.	f	\N
2449	577	Collaborative efforts among various scientific fields enhance the effectiveness of solutions to complex problems like climate change.	t	\N
2450	578	The laws of thermodynamics	f	\N
2451	578	The principle of superposition	f	\N
2452	578	The standard model of particle physics	f	\N
2453	578	Einstein's theory of relativity	t	\N
2454	579	To highlight the interconnectedness of various scientific principles and the importance of interdisciplinary research.	t	\N
2455	579	To argue that physical sciences are ultimately subjective and depend on individual interpretations.	f	\N
2456	579	To provide a detailed analysis of specific physical laws and their mathematical formulations.	f	\N
2457	579	To explain the historical developments in physical sciences and their impact on society.	f	\N
2458	580	Discrete sections highlighting individual historical figures.	f	\N
2459	580	Chronological order emphasizing the sequence of events.	t	\N
2460	580	Thematic organization focusing on technological advancements.	f	\N
2461	580	Comparative analysis linking different cultural effects.	f	\N
2462	581	The emphasis on humanism during the Renaissance encouraged scientific exploration.	t	\N
2463	581	The Renaissance stifled scientific innovation due to its focus on art.	f	\N
2464	581	The Renaissance had no significant impact on science according to the passage.	f	\N
2465	581	Scientific advancements were divorced from the intellectual climate of the Renaissance.	f	\N
2466	582	The spinning jenny	f	\N
2467	582	The mechanical clock	f	\N
2468	582	The steam engine	f	\N
2469	582	The printing press	t	\N
2470	583	To illustrate the interconnectedness of major historical events and their impacts on society.	t	\N
2471	583	To provide a detailed timeline of important inventions in history.	f	\N
2472	583	To highlight the negative consequences of exploration and industrialization.	f	\N
2473	583	To argue against the notion that art influences scientific progress.	f	\N
2474	584	Optimism	t	\N
2475	584	Pessimism	f	\N
2476	584	Social isolation	f	\N
2477	584	Cognitive inflexibility	f	\N
2478	585	The use of technology in psychology eliminates the need for human therapists.	f	\N
2479	585	Privacy concerns regarding digital tools are unfounded and negligible.	f	\N
2480	585	All digital mental health tools are considered effective and reliable.	f	\N
2481	585	Technology can improve access to mental health services for a wider audience.	t	\N
2482	586	Humanistic Therapy	f	\N
2483	586	Cognitive-Behavioral Therapy	t	\N
2484	586	Gestalt Therapy	f	\N
2485	586	Psychoanalysis	f	\N
2486	587	35, 15	t	A
2487	587	30, 12	f	B
2488	587	25, 10	f	C
2489	587	35, 20	f	A
2490	587	25, 15	t	B
2491	587	40, 5	f	C
2492	588	Yes, but it's close to the Operations department's ratio.	f	\N
2493	588	Yes, but it's close to the Operations department's ratio.	f	\N
2494	588	Yes, but it's close to the Operations department's ratio.	f	\N
2495	589	35	t	A
2496	589	30	f	B
2497	589	40	f	C
2498	589	10	t	A
2499	589	8	f	B
2500	589	12	f	C
2501	590	Product B	f	A
2502	590	Product A	t	B
2503	590	Product C	f	C
2504	590	200	t	A
2505	590	300	f	B
2506	590	100	f	C
2507	591	12000	f	A
2508	591	17500	t	B
2509	591	16500	f	C
2510	591	19000	f	A
2511	591	18000	f	B
2512	591	19500	t	C
2513	592	Automation will eliminate the need for a skilled workforce in logistics.	f	\N
2514	592	Job displacement is expected to be minimal with the integration of automation.	f	\N
2515	592	Companies should prioritize technology over workforce training to maximize efficiency.	f	\N
2516	592	A balanced approach requires investment in both technology and employee development.	t	\N
2517	592	All workforce impacts must be disregarded to focus on technology advancement.	f	\N
2518	593	Automation will eliminate the need for a skilled workforce in logistics.	f	\N
2519	593	Job displacement is expected to be minimal with the integration of automation.	f	\N
2520	593	Companies should prioritize technology over workforce training to maximize efficiency.	f	\N
2521	593	A balanced approach requires investment in both technology and employee development.	t	\N
2522	593	All workforce impacts must be disregarded to focus on technology advancement.	f	\N
2523	594	The West region has the highest market share.	f	\N
2524	594	The West region has the highest market share.	f	\N
2525	594	The West region has the highest market share.	f	\N
2526	595	5000	f	A
2527	595	9000	f	B
2528	595	7000	t	C
2529	595	20000	f	A
2530	595	15000	f	B
2531	595	30000	t	C
2532	596	5.0\\%, 8.0\\%	f	A
2533	596	4.7\\%, 7.0\\%	t	B
2534	596	4.5\\%, 6.5\\%	f	C
2535	596	5.5\\%, 7.5\\%	f	A
2536	596	4.0\\%, 6.0\\%	f	B
2537	596	3.5\\%, 5.0\\%	t	C
2538	597	50000	t	A
2539	597	45000	f	B
2540	597	55000	f	C
2541	597	42000	f	A
2542	597	38000	f	B
2543	597	40000	t	C
2544	598	The performance rating for the South region indicates its sales are acceptable.	f	\N
2545	598	The performance rating for the South region indicates its sales are acceptable.	f	\N
2546	598	The performance rating for the South region indicates its sales are acceptable.	f	\N
2547	599	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
2548	599	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
2549	599	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	f	\N
2550	599	EITHER statement ALONE is sufficient	f	\N
2551	599	Statements (1) and (2) TOGETHER are NOT sufficient	t	\N
2552	600	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
2553	600	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
2554	600	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	f	\N
2555	600	EITHER statement ALONE is sufficient	t	\N
2556	600	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
2557	601	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	t	\N
2558	601	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
2559	601	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	f	\N
2560	601	EITHER statement ALONE is sufficient	f	\N
2561	601	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
2562	602	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
2563	602	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
2564	602	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	t	\N
2565	602	EITHER statement ALONE is sufficient	f	\N
2566	602	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
2567	603	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
2568	603	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
2569	603	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	t	\N
2570	603	EITHER statement ALONE is sufficient	f	\N
2571	603	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
2572	604	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
2573	604	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
2574	604	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	t	\N
2575	604	EITHER statement ALONE is sufficient	f	\N
2576	604	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
2577	605	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
2578	605	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
2579	605	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	t	\N
2580	605	EITHER statement ALONE is sufficient	f	\N
2581	605	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
2582	606	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	t	\N
2583	606	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
2584	606	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	f	\N
2585	606	EITHER statement ALONE is sufficient	f	\N
2586	606	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
2587	607	Not Acceptable	f	\N
2588	607	Not Acceptable	f	\N
2589	608	No	f	\N
2590	608	No	f	\N
3250	755	Plants in harsh environments cannot compete with those in more favorable conditions.	f	\N
3251	756	The first statement is a counterargument; the second supports the conclusion.	f	\N
3252	756	The first statement is a general assumption; the second is an example.	f	\N
3253	756	The first statement is a conclusion; the second is a counterargument.	f	\N
3254	756	The first statement is a premise; the second is a counter to the premise.	t	\N
3255	756	The first statement is a premise; the second is a conclusion.	f	\N
3256	757	Mr. Lee's argument presents an assumption that stricter regulations will always lead to increased costs for businesses.	f	\N
3257	757	Mr. Lee's argument serves as a premise supporting the idea that stricter regulations could harm economic growth.	f	\N
3258	757	Mr. Lee's argument is a conclusion drawn from the evidence provided by Ms. Johnson about air quality improvements.	f	\N
3259	757	Mr. Lee's argument acts as a counterpoint to Ms. Johnson's claim about the benefits of stricter regulations.	t	\N
3260	757	Mr. Lee's argument suggests that environmental regulations are unnecessary in countries with good air quality.	f	\N
3261	758	Cultural greetings reflect underlying social values and can vary widely between societies.	t	\N
3262	758	All cultures agree on the importance of eye contact and physical greetings.	f	\N
3263	758	Greeting behaviors have little impact on the effectiveness of social interactions.	f	\N
3264	758	Understanding cultural differences in greetings is unnecessary for social interactions.	f	\N
3265	758	Respect is always shown through the same gestures across different cultures.	f	\N
3266	759	Evidence of the protagonist's eventual success in a male-dominated field	f	\N
3267	759	Assumption that the protagonist is representative of all female artists	f	\N
3268	759	Counterargument to the notion that women are successfully breaking barriers	f	\N
3269	759	Conclusion about the impact of patriarchal society on female artists	f	\N
3270	759	Premise supporting the artist's struggles against societal norms	t	\N
3271	760	It introduces the main concern regarding the legitimacy of street art.	f	\N
3272	760	It serves as a supporting premise for the argument in favor of street art.	t	\N
3273	760	It functions as the conclusion of the argument presented.	f	\N
3274	760	It presents a counterargument to the critics' viewpoint.	f	\N
3275	760	It highlights the negative effects of street art on community standards.	f	\N
3276	761	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
3277	761	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
3278	761	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	t	\N
3279	761	EITHER statement ALONE is sufficient	f	\N
3280	761	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
3281	762	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
3282	762	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
3283	762	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	t	\N
3284	762	EITHER statement ALONE is sufficient	f	\N
3285	762	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
3286	763	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
3287	763	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
3288	763	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	f	\N
3289	763	EITHER statement ALONE is sufficient	f	\N
3290	763	Statements (1) and (2) TOGETHER are NOT sufficient	t	\N
3291	765	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	t	\N
3292	765	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
3293	765	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	f	\N
3294	765	EITHER statement ALONE is sufficient	f	\N
3295	765	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
3296	766	Savings: $100.0, Profit: $-25.0	t	\N
3297	766	Savings: $80.0, Profit: $-20.0	f	\N
3298	766	Savings: $100.0, Profit: $-30.0	t	\N
3299	766	Savings: $120.0, Profit: $-40.0	f	\N
3300	767	2.5	f	\N
3301	767	6.0	f	\N
3302	767	3.0	t	\N
3303	767	4.0	f	\N
3304	768	500	f	\N
3305	768	520	t	\N
3306	768	460	f	\N
3307	768	540	f	\N
3308	769	9600.00	f	\N
3309	769	8800.00	t	\N
3310	769	9200.00	f	\N
3311	769	8400.00	f	\N
3312	770	19550.00	f	\N
3313	770	20700.00	t	\N
3314	770	22770.00	f	\N
3315	770	16100.00	f	\N
3316	771	12000	t	\N
3317	771	10000	f	\N
3318	771	13000	f	\N
3319	771	17000	f	\N
3320	772	-13000	f	\N
3321	772	-5000	f	\N
3322	772	0	f	\N
3323	772	-10000	t	\N
3324	773	0.84	f	\N
3325	773	1.04	t	\N
3326	773	1.54	f	\N
3327	773	2.08	f	\N
3328	774	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
3329	774	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
3330	774	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	f	\N
3535	815	62.0	f	\N
2591	609	20	t	\N
2592	609	10	f	\N
2593	609	10	f	\N
2594	609	25	f	\N
2595	610	10.0\\$	f	\N
2596	610	8.0\\$	f	\N
2597	610	12.0\\$	t	\N
2598	610	15.0\\$	f	\N
2599	611	63.8	f	\N
2600	611	64.68	f	\N
2601	611	53.8	f	\N
2602	611	58.8	t	\N
2603	611	52.92	f	\N
2604	612	11	f	\N
2605	612	8	f	\N
2606	612	10	f	\N
2607	612	9	t	\N
2608	614	9.4x	f	\N
2609	614	4.7x	t	\N
2610	614	4.6x	f	\N
2611	614	5.7x	f	\N
2612	615	x >= 1500, y >= 1200, x + y <= 3000	t	\N
2613	615	x >= 1500, y <= 1200, x + y <= 3000	f	\N
2614	615	x >= 1500, y >= 1200, x + y >= 3000	f	\N
2615	615	x < 1500, y >= 1200, x + y <= 3000	f	\N
2616	615	x >= 1300, y >= 1200, x + y <= 3000	f	\N
2617	616	4	f	\N
2618	616	6	f	\N
2619	616	2	f	\N
2620	616	5	t	\N
2621	617	17.5	f	\N
2622	617	26.76	f	\N
2623	617	25.4	t	\N
2624	617	13.77	f	\N
2625	618	6.0 kg	t	\N
2626	618	5.0 kg	f	\N
2627	618	8.0 kg	f	\N
2628	618	3.0 kg	f	\N
2629	618	9.0 kg	f	\N
2630	619	6	f	\N
2631	619	6	f	\N
2632	619	8	t	\N
2633	619	10	f	\N
2634	619	7	f	\N
2635	620	32	t	\N
2636	620	22	f	\N
2637	620	35	f	\N
2638	620	37	f	\N
2639	621	1200.00	t	\N
2640	621	1200.00	t	\N
2641	621	1600.00	f	\N
2642	621	945.00	f	\N
2643	622	120.0 pounds	f	\N
2644	622	250.0 pounds	f	\N
2645	622	200.0 pounds	f	\N
2646	622	150.0 pounds	t	\N
2647	623	140 km/h	f	\N
2648	623	150 km/h	f	\N
2649	623	130 km/h	f	\N
2650	623	135 km/h	t	\N
2651	624	8.68 hours	f	\N
2652	624	9.18 hours	f	\N
2653	624	9.81 hours	f	\N
2654	624	9.09 hours	t	\N
2655	625	\\$1500	f	\N
2656	625	\\$1500	f	\N
2657	625	\\$1450	t	\N
2658	625	\\$1350	f	\N
2659	626	2.67 kg	t	\N
2660	626	2.33 kg	f	\N
2661	626	1.83 kg	f	\N
2662	626	3.67 kg	f	\N
2663	627	40.0	t	\N
2664	627	50.0	f	\N
2665	627	30.0	f	\N
2666	627	30.0	f	\N
2667	628	90	f	\N
2668	628	104	f	\N
2669	628	96	f	\N
2670	628	100	t	\N
2671	629	37	f	\N
2672	629	30	f	\N
2673	629	32	t	\N
2674	629	42	f	\N
2675	629	29	f	\N
2676	630	15x + 25y >= 3000 and x + y >= 200	f	\N
2677	630	15x + 25y > 3000 and x + y < 200	f	\N
2678	630	15x + 20y >= 3000 and x + y <= 200	f	\N
2679	630	15x + 25y >= 3000 and x + y <= 200	t	\N
2680	631	$2572.81	f	\N
2681	631	$2422.81	f	\N
2682	631	$2522.81	t	\N
2683	631	$2322.81	f	\N
2684	632	Societal norms are increasingly ignoring utilitarian principles.	f	\N
2685	632	Utilitarianism has no significant influence on public policy.	f	\N
2686	632	Utilitarian principles likely contribute to a more collective approach in ethical decision-making.	t	\N
2687	632	Individual rights are prioritized over the well-being of the majority in utilitarian ethics.	f	\N
2688	632	Utilitarianism has been completely rejected in modern ethical discussions.	f	\N
2689	633	Physical activity can also lead to injuries if not managed properly.	f	\N
2690	633	Most students prefer sedentary activities over physical exercise.	f	\N
2691	633	Research shows that students who engage in physical activity have lower stress levels.	t	\N
2692	633	Increased physical activity leads to higher academic performance among students.	f	\N
2693	633	Many students are unable to participate in sports due to various barriers.	f	\N
2694	634	Social media is leading to more face-to-face interactions among teenagers.	f	\N
2695	634	Traditional media sources are gaining popularity among the youth.	f	\N
2696	634	Teenagers prefer obtaining information from books rather than online sources.	f	\N
2697	634	Teenagers are increasingly sharing experiences online over traditional communication methods.	t	\N
2698	634	Social media has no significant effect on the way teenagers connect with each other.	f	\N
2699	635	The findings support the idea that using libraries correlates with increased civic participation.	t	\N
2700	635	Access to public libraries has no relationship with community voting rates.	f	\N
2701	635	Public libraries are essential for fostering civic engagement among residents.	f	\N
2702	635	Only well-resourced libraries contribute to democratic processes in their communities.	f	\N
2703	635	Individuals who use public libraries are more likely to have higher levels of education.	f	\N
2704	636	The debate on moral relativism is irrelevant to contemporary ethical considerations.	f	\N
2705	636	Critics of moral relativism argue for the necessity of universal moral standards to prevent harm.	t	\N
2706	636	Moral relativism suggests that all moral frameworks are equally valid regardless of their principles.	f	\N
2707	636	Moral relativism supports the idea that ethical practices can remain unchanged over time.	f	\N
2708	636	Proponents of moral relativism believe that only one cultural perspective should dominate moral discussions.	f	\N
2709	637	Ethical decisions are best made by considering the greatest good for the greatest number.	f	\N
2710	637	All moral actions must prioritize individual happiness over collective well-being.	f	\N
2711	637	Moral rights and duties are always determined by the consequences of actions.	f	\N
2712	637	Consequentialist theories provide a stronger framework for moral decision-making.	f	\N
2713	637	There are actions that are inherently right or wrong regardless of outcomes.	t	\N
2714	638	Individuals can only maintain their cultural identity by completely rejecting outside influences.	f	\N
2715	638	Cultural practices evolve in response to external influences while still being embraced by individuals.	t	\N
2716	638	Cultural identity is solely based on rigid traditions that remain unchanged over time.	f	\N
2717	638	The transformation of culture is a recent phenomenon that has no historical precedent.	f	\N
2718	638	Cultural identity is only valuable when it remains static and unchanging.	f	\N
2719	639	initiated a new era of artistic expression and scientific exploration.	t	\N
2720	639	had minimal effects on the development of modern society.	f	\N
2721	639	led to a decline in philosophical thought and innovation.	f	\N
2722	639	restricted the progress of technology and science.	f	\N
2723	639	was solely focused on returning to ancient Greek art styles.	f	\N
2724	640	Prior to the printing press, handwritten manuscripts were limited to a small audience, limiting the spread of knowledge.	f	\N
2725	640	Many artists during the Renaissance were inspired by classical texts that were made widely available through printed materials.	t	\N
2726	640	The economic prosperity of cities during the Renaissance allowed for greater investment in literature and education.	f	\N
2727	640	The Renaissance was marked by a decline in religious influence, leading to a new focus on secular ideas.	f	\N
2728	640	The printing press was used exclusively for religious texts, contributing little to secular knowledge.	f	\N
2729	641	These scientific principles are essential for the development of innovative technologies, such as renewable energy and quantum computing.	t	\N
2730	641	Scientific advances in physics are solely confined to theoretical frameworks and do not translate into practical applications.	f	\N
2731	641	Understanding these concepts is primarily important for academic purposes and does not influence real-world technology.	f	\N
2732	641	The principles of physical sciences have no significant impact on contemporary technological applications.	f	\N
2733	642	The principles of quantum mechanics are confirmed by classical physics, providing no significant change in our understanding of reality.	f	\N
2734	642	The theories in quantum mechanics support the idea that reality operates solely on deterministic principles.	f	\N
2735	642	Quantum mechanics leads to practical benefits only, without affecting theoretical frameworks.	f	\N
2736	642	Quantum mechanics fundamentally alters our perception of reality by introducing concepts such as wave-particle duality and entanglement.	t	\N
2737	643	Maxwell's equations emphasize that electric currents cannot generate magnetic fields.	f	\N
2738	643	Maxwell's equations provide an argument that electricity and magnetism are completely independent phenomena.	f	\N
2739	643	Maxwell's equations describe how electric charges create electric fields.	t	\N
2740	643	Maxwell's equations state that electric fields do not influence magnetic fields.	f	\N
2741	644	The argument asserts that physical sciences operate independently of each other, thus emphasizing the uniqueness of each field.	f	\N
2742	644	The argument emphasizes that all physical phenomena are governed by strict deterministic laws, limiting the scope of scientific inquiry.	f	\N
2743	644	The argument highlights how advancements in one scientific field can lead to breakthroughs in others, demonstrating their mutual reliance.	t	\N
2744	644	The argument suggests that the complexities of climate change can be resolved through singular scientific approaches, reinforcing a limited perspective.	f	\N
2745	645	Single-discipline studies are deemed sufficient to tackle environmental issues on their own.	f	\N
2746	645	Interdisciplinary research is primarily motivated by funding opportunities rather than a genuine interest in scientific collaboration.	f	\N
2747	645	Interdisciplinary research is considered less important than traditional approaches focused solely on physical sciences.	f	\N
2748	645	Collaborative efforts among various scientific fields enhance the effectiveness of solutions to complex problems like climate change.	t	\N
2749	646	The laws of thermodynamics	f	\N
2750	646	The principle of superposition	f	\N
2751	646	The standard model of particle physics	f	\N
2752	646	Einstein's theory of relativity	t	\N
2753	647	To highlight the interconnectedness of various scientific principles and the importance of interdisciplinary research.	t	\N
2754	647	To argue that physical sciences are ultimately subjective and depend on individual interpretations.	f	\N
2755	647	To provide a detailed analysis of specific physical laws and their mathematical formulations.	f	\N
2756	647	To explain the historical developments in physical sciences and their impact on society.	f	\N
2757	648	Discrete sections highlighting individual historical figures.	f	\N
2758	648	Chronological order emphasizing the sequence of events.	t	\N
2759	648	Thematic organization focusing on technological advancements.	f	\N
2760	648	Comparative analysis linking different cultural effects.	f	\N
2761	649	The emphasis on humanism during the Renaissance encouraged scientific exploration.	t	\N
2762	649	The Renaissance stifled scientific innovation due to its focus on art.	f	\N
2763	649	The Renaissance had no significant impact on science according to the passage.	f	\N
2764	649	Scientific advancements were divorced from the intellectual climate of the Renaissance.	f	\N
2765	650	The spinning jenny	f	\N
2766	650	The mechanical clock	f	\N
2767	650	The steam engine	f	\N
2768	650	The printing press	t	\N
2769	651	To illustrate the interconnectedness of major historical events and their impacts on society.	t	\N
2770	651	To provide a detailed timeline of important inventions in history.	f	\N
2771	651	To highlight the negative consequences of exploration and industrialization.	f	\N
2772	651	To argue against the notion that art influences scientific progress.	f	\N
2773	652	Optimism	t	\N
2774	652	Pessimism	f	\N
2775	652	Social isolation	f	\N
2776	652	Cognitive inflexibility	f	\N
2777	653	The use of technology in psychology eliminates the need for human therapists.	f	\N
2778	653	Privacy concerns regarding digital tools are unfounded and negligible.	f	\N
2779	653	All digital mental health tools are considered effective and reliable.	f	\N
2780	653	Technology can improve access to mental health services for a wider audience.	t	\N
2781	654	Humanistic Therapy	f	\N
2782	654	Cognitive-Behavioral Therapy	t	\N
2783	654	Gestalt Therapy	f	\N
2784	654	Psychoanalysis	f	\N
2785	655	35, 15	t	A
2786	655	30, 12	f	B
2787	655	25, 10	f	C
2788	655	35, 20	f	A
2789	655	25, 15	t	B
2790	655	40, 5	f	C
2791	656	Yes, but it's close to the Operations department's ratio.	f	\N
2792	656	Yes, but it's close to the Operations department's ratio.	f	\N
2793	656	Yes, but it's close to the Operations department's ratio.	f	\N
2794	657	35	t	A
2795	657	30	f	B
2796	657	40	f	C
2797	657	10	t	A
2798	657	8	f	B
2799	657	12	f	C
2800	658	Product B	f	A
2801	658	Product A	t	B
2802	658	Product C	f	C
2803	658	200	t	A
2804	658	300	f	B
2805	658	100	f	C
2806	659	12000	f	A
2807	659	17500	t	B
2808	659	16500	f	C
2809	659	19000	f	A
2810	659	18000	f	B
2811	659	19500	t	C
2812	660	Automation will eliminate the need for a skilled workforce in logistics.	f	\N
2813	660	Job displacement is expected to be minimal with the integration of automation.	f	\N
2814	660	Companies should prioritize technology over workforce training to maximize efficiency.	f	\N
2815	660	A balanced approach requires investment in both technology and employee development.	t	\N
2816	660	All workforce impacts must be disregarded to focus on technology advancement.	f	\N
2817	661	Automation will eliminate the need for a skilled workforce in logistics.	f	\N
2818	661	Job displacement is expected to be minimal with the integration of automation.	f	\N
2819	661	Companies should prioritize technology over workforce training to maximize efficiency.	f	\N
2820	661	A balanced approach requires investment in both technology and employee development.	t	\N
2821	661	All workforce impacts must be disregarded to focus on technology advancement.	f	\N
2822	662	The West region has the highest market share.	f	\N
2823	662	The West region has the highest market share.	f	\N
2824	662	The West region has the highest market share.	f	\N
2825	663	5000	f	A
2826	663	9000	f	B
2827	663	7000	t	C
2828	663	20000	f	A
2829	663	15000	f	B
2830	663	30000	t	C
2831	664	5.0\\%, 8.0\\%	f	A
2832	664	4.7\\%, 7.0\\%	t	B
2833	664	4.5\\%, 6.5\\%	f	C
2834	664	5.5\\%, 7.5\\%	f	A
2835	664	4.0\\%, 6.0\\%	f	B
2836	664	3.5\\%, 5.0\\%	t	C
2837	665	50000	t	A
2838	665	45000	f	B
2839	665	55000	f	C
2840	665	42000	f	A
2841	665	38000	f	B
2842	665	40000	t	C
2843	666	The performance rating for the South region indicates its sales are acceptable.	f	\N
2844	666	The performance rating for the South region indicates its sales are acceptable.	f	\N
2845	666	The performance rating for the South region indicates its sales are acceptable.	f	\N
2846	667	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
2847	667	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
2848	667	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	f	\N
2849	667	EITHER statement ALONE is sufficient	f	\N
2850	667	Statements (1) and (2) TOGETHER are NOT sufficient	t	\N
2851	668	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
2852	668	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
2853	668	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	f	\N
2854	668	EITHER statement ALONE is sufficient	t	\N
2855	668	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
2856	669	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	t	\N
2857	669	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
2858	669	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	f	\N
2859	669	EITHER statement ALONE is sufficient	f	\N
2860	669	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
2861	670	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
2862	670	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
2863	670	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	t	\N
2864	670	EITHER statement ALONE is sufficient	f	\N
2865	670	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
2866	671	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
2867	671	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
2868	671	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	t	\N
2869	671	EITHER statement ALONE is sufficient	f	\N
2870	671	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
2871	672	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
2872	672	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
2873	672	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	t	\N
2874	672	EITHER statement ALONE is sufficient	f	\N
2875	672	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
2876	673	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
2877	673	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
2878	673	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	t	\N
2879	673	EITHER statement ALONE is sufficient	f	\N
2880	673	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
2881	674	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	t	\N
2882	674	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
2883	674	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	f	\N
2884	674	EITHER statement ALONE is sufficient	f	\N
2885	674	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
2886	675	Not Acceptable	f	\N
2887	675	Not Acceptable	f	\N
2888	676	No	f	\N
2889	676	No	f	\N
3331	774	EITHER statement ALONE is sufficient	t	\N
3332	774	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
3333	776	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	t	\N
3334	776	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
3335	776	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	f	\N
3336	776	EITHER statement ALONE is sufficient	f	\N
3337	776	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
3338	777	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
3339	777	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
3340	777	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	t	\N
3341	777	EITHER statement ALONE is sufficient	f	\N
3342	777	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
3343	778	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
3344	778	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
3345	778	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	f	\N
3346	778	EITHER statement ALONE is sufficient	f	\N
3347	778	Statements (1) and (2) TOGETHER are NOT sufficient	t	\N
3348	779	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	t	\N
3349	779	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
3350	779	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	f	\N
3351	779	EITHER statement ALONE is sufficient	f	\N
3352	779	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
3353	780	1358.85	f	\N
3354	780	1714.74	f	\N
3355	780	779.42	f	\N
3356	780	1558.85	t	\N
3357	782	Approximately 37.37%	f	\N
3358	782	Approximately 50.67%	t	\N
3359	782	Approximately 57.37%	f	\N
3360	782	Approximately 27.37%	f	\N
3361	783	Approximately 1.36	f	\N
3362	783	Approximately 1.53	t	\N
3363	783	Approximately 1.16	f	\N
3364	783	Approximately 1.66	f	\N
3365	784	16.00\\%	t	\N
3366	784	-4.00\\%	f	\N
3367	784	800.00	f	\N
3368	784	13.79\\%	f	\N
3369	785	7.00	f	\N
3370	785	5.80	f	\N
3371	785	5.60	t	\N
3372	785	7.00	f	\N
3373	786	45.10	f	\N
3374	786	55.07	t	\N
3375	786	60.25	f	\N
3376	786	54.17	f	\N
3377	787	26.84	t	\N
3378	787	24.00	f	\N
3379	787	28.50	f	\N
3380	787	30.75	f	\N
3381	788	consistent	f	A
3382	788	erratic	f	B
3383	788	anomalous	f	C
3384	788	multifaceted	t	D
3385	788	harmony	f	A
3386	788	cognitive dissonance	t	B
3387	788	conflict	f	C
3388	788	strategy	f	D
3389	789	solitude	f	\N
3390	789	contentment	f	\N
3391	789	betrayal	f	\N
3392	789	joy	f	\N
3393	789	companionship	t	\N
3394	789	loneliness	t	\N
3395	790	constraining	f	\N
3396	790	neutral	t	\N
3397	790	detrimental	f	\N
3398	790	volatile	f	\N
3399	790	problematic	f	\N
3400	790	catalytic	t	\N
3401	791	wonder	f	\N
3402	791	speculate	t	\N
3403	791	celebrate	f	\N
3404	791	ignore	f	\N
3405	791	confirm	f	\N
3406	791	document	f	\N
3407	792	dissension	t	A
3408	792	harmony	f	B
3409	792	collaboration	f	C
3410	792	resolution	f	D
3411	792	stable	f	A
3412	792	dynamic	f	B
3413	792	conducive	f	C
3414	792	volatile	t	D
3415	792	ineffective	t	A
3416	792	robust	f	B
3417	792	efficient	f	C
3418	792	effective	f	D
3419	793	isolated	f	\N
3420	793	manageable	t	\N
3421	793	perpetual	f	\N
3422	793	untreatable	f	\N
3423	793	preventable	t	\N
3424	793	intrusive	f	\N
3425	794	Thought patterns directly lead to changes in emotional and behavioral responses.	t	\N
3426	794	Cognitive distortions can be easily recognized by individuals.	f	\N
3427	794	Emotional responses are not influenced by cognitive processes.	f	\N
3428	794	There is no connection between thought and emotion.	f	\N
3429	795	Social psychology ignores the impact of group dynamics on individual behavior.	f	\N
3430	795	Social psychology examines how individuals are influenced by the presence of others.	t	\N
3431	795	Social psychology focuses solely on prejudice and discrimination.	f	\N
3432	795	Social psychology primarily addresses individual cognitive processes.	f	\N
3433	796	All individuals have the same childhood experiences regardless of their environment.	f	\N
3434	796	Early interactions with caregivers have a lasting impact on emotional development.	t	\N
3435	796	Developmental changes occur in a linear, unchanging manner.	f	\N
3436	796	Early childhood experiences are irrelevant to adult behavior.	f	\N
2890	677	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
2891	677	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	t	\N
2892	677	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	f	\N
2893	677	EITHER statement ALONE is sufficient	f	\N
2894	677	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
2895	678	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
2896	678	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
2897	678	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	f	\N
2898	678	EITHER statement ALONE is sufficient	f	\N
2899	678	Statements (1) and (2) TOGETHER are NOT sufficient	t	\N
2900	679	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	t	\N
2901	679	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
2902	679	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	f	\N
2903	679	EITHER statement ALONE is sufficient	f	\N
2904	679	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
2905	681	629.86	t	\N
2906	681	620.00	t	\N
2907	681	640.00	f	\N
2908	681	580.00	f	\N
2909	682	It is possible to achieve a sum of 18.	f	\N
2910	682	There are a total of 9 unique sums formed.	t	\N
2911	682	There are a total of 6 unique sums formed.	f	\N
2912	682	There are a total of 10 unique sums.	f	\N
2913	683	$7.25	f	\N
2914	683	$8.75	f	\N
2915	683	$8.25	t	\N
2916	683	$10.25	f	\N
2917	684	350.0 for $6000 and 324.99999999999994 for $7000	f	\N
2918	684	300.0 for $6000 and 349.99999999999994 for $7000	t	\N
2919	684	300.0 for $6000 and 324.99999999999994 for $7000	f	\N
2920	684	350.0 for $6000 and 349.99999999999994 for $7000	f	\N
2921	685	340.0 for 6% and 450.0 for 7%	f	\N
2922	685	340.0 for 6% and 400.0 for 7%	t	\N
2923	685	320.0 for 6% and 400.0 for 7%	f	\N
2924	685	320.0 for 6% and 450.0 for 7%	f	\N
2925	686	23.08	t	\N
2926	686	26.05	f	\N
2927	686	25.25	f	\N
2928	686	20.15	f	\N
2929	687	59404.26	f	\N
2930	687	55761.55	f	\N
2931	687	52337.70	f	\N
2932	687	55200	t	\N
2933	688	28.26	f	\N
2934	688	27.1	f	\N
2935	688	27.5	t	\N
2936	688	26.06	f	\N
2937	689	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	t	\N
2938	689	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
2939	689	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	f	\N
2940	689	EITHER statement ALONE is sufficient	f	\N
2941	689	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
2942	690	Pair (3, 5): Sum = 8, Product = 15 (Incorrect: sum != product)	f	\N
2943	690	Pair (1, 12): Sum = 13, Product = 12 (Incorrect: sum != product)	f	\N
2944	690	All pairs are valid since at least one must be correct (Incorrect conclusion)	f	\N
2945	690	Pair (4, 2): Sum = 6, Product = 8 (Incorrect: sum != product)	f	\N
2946	691	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
2947	691	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
2948	691	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	t	\N
2949	691	EITHER statement ALONE is sufficient	f	\N
2950	691	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
2951	692	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	t	\N
2952	692	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
2953	692	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	f	\N
2954	692	EITHER statement ALONE is sufficient	f	\N
2955	692	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
2956	693	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
2957	693	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
2958	693	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	f	\N
2959	693	EITHER statement ALONE is sufficient	f	\N
2960	693	Statements (1) and (2) TOGETHER are NOT sufficient	t	\N
2961	694	6 combinations and 12 permutations	t	\N
2962	694	5 combinations and 24 permutations	f	\N
2963	694	7 combinations and 12 permutations	f	\N
2964	694	6 combinations and 16 permutations	f	\N
2965	697	8%	t	\N
2966	697	6%	f	\N
2967	697	3%	f	\N
2968	697	10%	f	\N
2969	698	30% (Correct) and 67.0%	t	\N
2970	698	40% and 67.0%	f	\N
2971	698	30% and 57.0%	f	\N
2972	698	30% and 72.0%	f	\N
2973	699	60 and 65.0%	f	\N
2974	699	60 (Correct) and 55.0%	t	\N
2975	699	65 and 55.0%	f	\N
2976	699	60 and 40.0%	f	\N
2977	700	The probability for Experiment 2 is 0.39, highest is 0.86, average is 0.52.	t	\N
2978	700	The probability for Experiment 2 is 0.4, highest is 0.85, average is 0.52.	f	\N
2979	700	The probability for Experiment 2 is 0.39, highest is 0.85, average is 0.5.	f	\N
2980	700	The probability for Experiment 2 is 0.4, highest is 0.86, average is 0.52.	f	\N
2981	701	The cumulative probability is 2.58, average is 0.52. The following experiment(s) had a probability greater than the average: Experiment 1, Experiment 5.	t	\N
2982	701	The cumulative probability is 2.58, average is 0.55. The following experiment(s) had a probability greater than the average: Experiment 1, Experiment 2.	f	\N
2983	701	The cumulative probability is 2.6, average is 0.52. The following experiment(s) had a probability greater than the average: Experiment 1, Experiment 5.	f	\N
2984	701	The cumulative probability is 2.6, average is 0.55. The following experiment(s) had a probability greater than the average: Experiment 1, Experiment 5.	f	\N
2985	702	7.5 employees	t	\N
2986	702	7.2 employees	f	\N
2987	702	8.2 employees	f	\N
2988	702	7.5 employees	t	\N
2989	703	45%	t	\N
2990	703	47%	f	\N
2991	703	51%	f	\N
2992	703	44%	f	\N
2993	704	superfluous	f	\N
2994	704	arcane	f	\N
2995	704	beneficial	f	\N
2996	704	urgent	t	\N
2997	704	optional	f	\N
2998	704	discreet	f	\N
2999	705	cognitive	f	A
3000	705	physical	f	B
3001	705	environmental	t	C
3002	705	genetic	f	D
3003	705	psychological	f	A
3004	705	sociocultural	t	B
3005	705	biological	f	C
3006	705	emotional	f	D
3007	706	subjective	t	A
3008	706	materialist	f	B
3009	706	transcendental	f	C
3010	706	objective	f	D
3011	706	rational	f	A
3012	706	literal	f	B
3013	706	emotional	t	C
3014	706	empirical	f	D
3015	706	symbolic	f	A
3016	706	metaphysical	t	B
3017	706	theoretical	f	C
3018	706	pragmatic	f	D
3019	707	balance	f	A
3020	707	predictability	f	B
3021	707	fluctuations	t	C
3022	707	harmony	f	D
3023	707	equities	f	A
3024	707	stability	f	B
3025	707	surpluses	f	C
3026	707	deficits	t	D
3027	707	minimal	f	A
3028	707	temporary	f	B
3029	707	severe	t	C
3030	707	chronic	f	D
3031	708	ambivalent	f	\N
3032	708	tentative	f	\N
3033	708	unequivocal	t	\N
3034	708	resounding	t	\N
3035	708	mixed	f	\N
3036	708	marginal	f	\N
3037	709	Research shows that UBI programs have often resulted in higher consumer spending.	f	\N
3038	709	Many economists believe that UBI can foster creative entrepreneurship.	f	\N
3039	709	Studies indicate that UBI has led to increased work participation in trials.	f	\N
3040	709	Long-term studies reveal that UBI can discourage people from seeking employment.	t	\N
3041	710	The benefits of globalization are often distributed unevenly, favoring developed nations.	t	\N
3042	710	Globalization benefits all nations equally, fostering balanced economic growth.	f	\N
3043	710	Technological advancements have no effect on the dynamics of globalization.	f	\N
3044	710	Protectionist policies are universally accepted as the best solution to economic disparities.	f	\N
3045	711	Public perception is always aligned with economic policies developed by governments.	f	\N
3046	711	Public perception has no impact on the implementation of economic policies.	f	\N
3047	711	Economic policies that fail to consider public sentiment are likely to face backlash.	t	\N
3048	711	Economic policies are primarily successful when they are supported by global consensus.	f	\N
3049	712	All individuals experience the same emotional outcomes regardless of early attachment experiences.	f	\N
3050	712	Early psychological development has no impact on future emotional well-being.	f	\N
3051	712	Positive early relationships can enhance later emotional health.	t	\N
3052	712	Emotional well-being is solely dependent on genetic factors.	f	\N
3053	713	The importance of mental disorders and their treatments.	f	\N
3054	713	The historical evolution of psychological theories.	f	\N
3055	713	The role of technology in psychological research.	f	\N
3056	713	The exploration of various subfields and their contributions to understanding human behavior.	t	\N
3057	714	Positive psychology is effective only for certain psychological disorders.	f	\N
3058	714	Individuals have the capacity to change their psychological state through intentional practices.	t	\N
3059	714	Happiness is solely a product of external circumstances.	f	\N
3060	714	All aspects of human behavior are predetermined by genetics.	f	\N
3061	715	Psychological subfields operate independently without relevance to one another.	f	\N
3062	715	The diversity of psychological approaches enhances the understanding of human behavior.	t	\N
3063	715	All psychological theories ultimately lead to the same treatment methodologies.	f	\N
3064	715	Emphasis on biological factors is paramount in psychological research.	f	\N
3065	716	rational	t	A
3066	716	conservative	f	B
3067	716	impulsive	f	C
3068	716	logical	f	D
3069	716	conventional	f	A
3070	716	fragmented	f	B
3071	716	nuanced	t	C
3072	716	simplistic	f	D
3073	717	perfunctory	f	\N
3074	717	unbiased	f	\N
3075	717	superficial	f	\N
3076	717	pertinent	t	\N
3077	717	irrelevant	f	\N
3078	717	impartial	t	\N
3079	718	supportive	f	\N
3080	718	derisive	f	\N
3081	718	apathy	f	\N
3082	718	indifferent	f	\N
3083	718	hostile	f	\N
3084	718	enthusiastic	t	\N
3085	719	impact	f	A
3086	719	nature	t	B
3087	719	mechanics	f	C
3088	719	complexity	f	D
3089	719	misleading	f	A
3090	719	unique	f	B
3091	719	fundamental	t	C
3092	719	superficial	f	D
3093	719	contradictory	f	A
3094	719	abstract	f	B
3095	719	competing	t	C
3096	719	empirical	f	D
3097	720	heroic	t	\N
3098	720	mythical	f	\N
3099	720	insignificant	f	\N
3100	720	mundane	f	\N
3101	720	antagonistic	f	\N
3102	720	tragic	f	\N
3103	721	primitive	f	\N
3104	721	narrow	f	\N
3105	721	comprehensive	t	\N
3106	721	chaotic	f	\N
3107	721	superficial	f	\N
3108	721	limited	f	\N
3109	722	Stevens embodies the triumph of duty over emotion, while Gatsby signifies the success of the American Dream.	f	\N
3110	722	The narratives suggest that personal connections are secondary to social status and wealth.	f	\N
3111	722	Both characters reject personal relationships in favor of their aspirations, leading to ultimate fulfillment.	f	\N
3112	722	Both characters experience profound loneliness as a consequence of their devotion to unattainable ideals.	t	\N
3113	723	Stevens' English estate symbolizes lost opportunities, while Gatsby's lavish parties represent the emptiness of wealth.	t	\N
3114	723	The rural landscapes in both novels signify the characters' connection to their past and future hopes.	f	\N
3115	723	Both settings reflect a period of prosperity, underscoring the characters' success and happiness.	f	\N
3116	723	Both settings act as reflections of the characters' inner turmoil and their struggles for identity.	f	\N
3117	724	The presence of written language and military strength	f	\N
3118	724	Geographic location and population density	f	\N
3119	724	Religious beliefs and trade relations	f	\N
3120	724	Innovations in engineering and civic participation	t	\N
3121	725	They emphasized the importance of divine rule over human governance.	f	\N
3122	725	They established the concept of democracy and citizenship rights.	t	\N
3123	725	They introduced the idea of a monarchy as the preferred political structure.	f	\N
3124	725	They demonstrated that governance can be based solely on military strength.	f	\N
3125	726	Governance played a vital role in fostering cultural achievements.	t	\N
3126	726	Cultural achievements often were independent of political structures.	f	\N
3127	726	The lack of written language hindered cultural advancements.	f	\N
3128	726	Ancient civilizations prioritized military achievements over cultural developments.	f	\N
3129	727	The rise of technology has completely replaced traditional political institutions.	f	\N
3130	727	Populism is the only political movement influencing contemporary politics.	f	\N
3131	727	Globalization has led to a more isolated national identity among countries.	f	\N
3132	727	The interplay of media, ideology, and globalization shapes modern political landscapes.	t	\N
3133	728	Media only serves as a platform for government propaganda.	f	\N
3134	728	Social media eliminates the role of traditional media in political discourse.	f	\N
3135	728	Misinformation can significantly distort public understanding of political realities.	t	\N
3136	728	Media has no significant impact on public perception of political issues.	f	\N
3137	729	Voters possess the ability to critically evaluate information from multiple sources.	t	\N
3138	729	All voters are equally informed regardless of the media they consume.	f	\N
3139	729	Misinformation is unlikely to affect voter behavior in elections.	f	\N
3140	729	Voters are predominantly influenced by traditional media outlets.	f	\N
3141	730	Voter apathy is the main challenge faced by modern democracies.	f	\N
3142	730	Political discourse is increasingly shaped by the interplay of various global and local influences.	t	\N
3143	730	The decline of traditional political parties is the sole outcome of globalization.	f	\N
3144	730	Media is irrelevant in shaping ideological beliefs within globalization.	f	\N
3437	797	Empiricism	t	\N
3438	797	Rationalism	f	\N
3439	797	Utilitarianism	f	\N
3440	797	Existentialism	f	\N
3441	798	The creation of identity through choices.	t	\N
3442	798	The preordained nature of individuals.	f	\N
3443	798	The importance of intellectual reasoning.	f	\N
3444	798	Conformity to societal norms.	f	\N
3445	799	Personal desires should guide moral decisions.	f	\N
3446	799	Moral actions are determined by their consequences.	f	\N
3447	799	Happiness is the ultimate goal of morality.	f	\N
3448	799	Ethical behavior is based on universal maxims.	t	\N
3449	800	revival	t	\N
3450	800	chaos	f	\N
3451	800	stagnation	f	\N
3452	800	decline	f	\N
3453	800	confusion	f	\N
3454	800	disruption	f	\N
3455	801	undermine	f	\N
3456	801	disregard	f	\N
3457	801	assess	f	\N
3458	801	marginalize	f	\N
3459	801	clarify	f	\N
3460	801	embrace	t	\N
3461	802	compassion	t	A
3462	802	indifference	f	B
3463	802	sacrilege	f	C
3464	802	generosity	f	D
3465	802	heroic	f	A
3466	802	nostalgic	f	B
3467	802	malevolent	f	C
3468	802	altruistic	t	D
3469	802	apologetic	f	A
3470	802	exemplary	t	B
3471	802	irresponsible	f	C
3472	802	exuberant	f	D
3473	803	ambiguous	f	\N
3474	803	transparent	f	\N
3475	803	confusing	f	\N
3476	803	incomprehensible	f	\N
3477	803	articulate	t	\N
3478	803	candid	t	\N
3479	804	inauthentic	f	A
3480	804	emotional	t	B
3481	804	physical	f	C
3482	804	observable	f	D
3483	804	identical	f	A
3484	804	external	t	B
3485	804	social	f	C
3486	804	self-referential	f	D
3487	804	ambiguity	f	A
3488	804	consistency	t	B
3489	804	discrepancy	f	C
3490	804	disharmony	f	D
3491	805	ambiguous	f	A
3492	805	superficial	f	B
3493	805	unquestioning	f	C
3494	805	critical	t	D
3495	805	articulate	f	A
3496	805	disregard	f	B
3497	805	ignore	f	C
3498	805	reassess	t	D
3499	806	GMOs require less pesticide, thus benefiting traditional methods.	f	\N
3500	806	Introducing GMOs diminishes biodiversity in ecosystems.	t	\N
3501	806	GMOs boost yields, which supports traditional agriculture practices.	f	\N
3145	731	145 cartridges, 43500 pages	f	\N
1993	473	20	t	\N
1994	473	10	f	\N
1995	473	10	f	\N
1996	473	25	f	\N
1997	474	10.0\\$	f	\N
1998	474	8.0\\$	f	\N
1999	474	12.0\\$	t	\N
2000	474	15.0\\$	f	\N
2001	475	63.8	f	\N
2002	475	64.68	f	\N
2003	475	53.8	f	\N
2004	475	58.8	t	\N
2005	475	52.92	f	\N
2006	476	11	f	\N
2007	476	8	f	\N
2008	476	10	f	\N
2009	476	9	t	\N
2010	478	9.4x	f	\N
2011	478	4.7x	t	\N
2012	478	4.6x	f	\N
2013	478	5.7x	f	\N
2014	479	x >= 1500, y >= 1200, x + y <= 3000	t	\N
2015	479	x >= 1500, y <= 1200, x + y <= 3000	f	\N
2016	479	x >= 1500, y >= 1200, x + y >= 3000	f	\N
2017	479	x < 1500, y >= 1200, x + y <= 3000	f	\N
2018	479	x >= 1300, y >= 1200, x + y <= 3000	f	\N
2019	480	4	f	\N
2020	480	6	f	\N
2021	480	2	f	\N
2022	480	5	t	\N
2023	481	17.5	f	\N
2024	481	26.76	f	\N
2025	481	25.4	t	\N
2026	481	13.77	f	\N
2027	482	6.0 kg	t	\N
2028	482	5.0 kg	f	\N
2029	482	8.0 kg	f	\N
2030	482	3.0 kg	f	\N
2031	482	9.0 kg	f	\N
2032	483	6	f	\N
2033	483	6	f	\N
2034	483	8	t	\N
2035	483	10	f	\N
2036	483	7	f	\N
2037	484	32	t	\N
2038	484	22	f	\N
2039	484	35	f	\N
2040	484	37	f	\N
2041	485	1200.00	t	\N
2042	485	1200.00	t	\N
2043	485	1600.00	f	\N
2044	485	945.00	f	\N
2045	486	120.0 pounds	f	\N
2046	486	250.0 pounds	f	\N
2047	486	200.0 pounds	f	\N
2048	486	150.0 pounds	t	\N
2049	487	140 km/h	f	\N
2050	487	150 km/h	f	\N
2051	487	130 km/h	f	\N
2052	487	135 km/h	t	\N
2053	488	8.68 hours	f	\N
2054	488	9.18 hours	f	\N
2055	488	9.81 hours	f	\N
2056	488	9.09 hours	t	\N
2057	489	\\$1500	f	\N
2058	489	\\$1500	f	\N
2059	489	\\$1450	t	\N
2060	489	\\$1350	f	\N
2061	490	2.67 kg	t	\N
2062	490	2.33 kg	f	\N
2063	490	1.83 kg	f	\N
2064	490	3.67 kg	f	\N
2065	491	40.0	t	\N
2066	491	50.0	f	\N
2067	491	30.0	f	\N
2068	491	30.0	f	\N
2069	492	90	f	\N
2070	492	104	f	\N
2071	492	96	f	\N
2072	492	100	t	\N
2073	493	37	f	\N
2074	493	30	f	\N
2075	493	32	t	\N
2076	493	42	f	\N
2077	493	29	f	\N
2078	494	15x + 25y >= 3000 and x + y >= 200	f	\N
2079	494	15x + 25y > 3000 and x + y < 200	f	\N
2080	494	15x + 20y >= 3000 and x + y <= 200	f	\N
2081	494	15x + 25y >= 3000 and x + y <= 200	t	\N
2082	495	$2572.81	f	\N
2083	495	$2422.81	f	\N
2084	495	$2522.81	t	\N
2085	495	$2322.81	f	\N
2086	496	Societal norms are increasingly ignoring utilitarian principles.	f	\N
2087	496	Utilitarianism has no significant influence on public policy.	f	\N
2088	496	Utilitarian principles likely contribute to a more collective approach in ethical decision-making.	t	\N
2089	496	Individual rights are prioritized over the well-being of the majority in utilitarian ethics.	f	\N
2090	496	Utilitarianism has been completely rejected in modern ethical discussions.	f	\N
2091	497	Physical activity can also lead to injuries if not managed properly.	f	\N
2092	497	Most students prefer sedentary activities over physical exercise.	f	\N
2093	497	Research shows that students who engage in physical activity have lower stress levels.	t	\N
2094	497	Increased physical activity leads to higher academic performance among students.	f	\N
2095	497	Many students are unable to participate in sports due to various barriers.	f	\N
2096	498	Social media is leading to more face-to-face interactions among teenagers.	f	\N
2097	498	Traditional media sources are gaining popularity among the youth.	f	\N
2098	498	Teenagers prefer obtaining information from books rather than online sources.	f	\N
2099	498	Teenagers are increasingly sharing experiences online over traditional communication methods.	t	\N
2100	498	Social media has no significant effect on the way teenagers connect with each other.	f	\N
2101	499	The findings support the idea that using libraries correlates with increased civic participation.	t	\N
2102	499	Access to public libraries has no relationship with community voting rates.	f	\N
2103	499	Public libraries are essential for fostering civic engagement among residents.	f	\N
2104	499	Only well-resourced libraries contribute to democratic processes in their communities.	f	\N
2105	499	Individuals who use public libraries are more likely to have higher levels of education.	f	\N
2106	500	The debate on moral relativism is irrelevant to contemporary ethical considerations.	f	\N
2107	500	Critics of moral relativism argue for the necessity of universal moral standards to prevent harm.	t	\N
2108	500	Moral relativism suggests that all moral frameworks are equally valid regardless of their principles.	f	\N
2109	500	Moral relativism supports the idea that ethical practices can remain unchanged over time.	f	\N
2110	500	Proponents of moral relativism believe that only one cultural perspective should dominate moral discussions.	f	\N
3146	731	150 cartridges, 45000 pages	f	\N
2111	501	Ethical decisions are best made by considering the greatest good for the greatest number.	f	\N
2112	501	All moral actions must prioritize individual happiness over collective well-being.	f	\N
2113	501	Moral rights and duties are always determined by the consequences of actions.	f	\N
2114	501	Consequentialist theories provide a stronger framework for moral decision-making.	f	\N
2115	501	There are actions that are inherently right or wrong regardless of outcomes.	t	\N
2116	502	Individuals can only maintain their cultural identity by completely rejecting outside influences.	f	\N
2117	502	Cultural practices evolve in response to external influences while still being embraced by individuals.	t	\N
2118	502	Cultural identity is solely based on rigid traditions that remain unchanged over time.	f	\N
2119	502	The transformation of culture is a recent phenomenon that has no historical precedent.	f	\N
2120	502	Cultural identity is only valuable when it remains static and unchanging.	f	\N
2121	503	initiated a new era of artistic expression and scientific exploration.	t	\N
2122	503	had minimal effects on the development of modern society.	f	\N
2123	503	led to a decline in philosophical thought and innovation.	f	\N
2124	503	restricted the progress of technology and science.	f	\N
2125	503	was solely focused on returning to ancient Greek art styles.	f	\N
2126	504	Prior to the printing press, handwritten manuscripts were limited to a small audience, limiting the spread of knowledge.	f	\N
2127	504	Many artists during the Renaissance were inspired by classical texts that were made widely available through printed materials.	t	\N
2128	504	The economic prosperity of cities during the Renaissance allowed for greater investment in literature and education.	f	\N
2129	504	The Renaissance was marked by a decline in religious influence, leading to a new focus on secular ideas.	f	\N
2130	504	The printing press was used exclusively for religious texts, contributing little to secular knowledge.	f	\N
2131	505	These scientific principles are essential for the development of innovative technologies, such as renewable energy and quantum computing.	t	\N
2132	505	Scientific advances in physics are solely confined to theoretical frameworks and do not translate into practical applications.	f	\N
2133	505	Understanding these concepts is primarily important for academic purposes and does not influence real-world technology.	f	\N
2134	505	The principles of physical sciences have no significant impact on contemporary technological applications.	f	\N
2135	506	The principles of quantum mechanics are confirmed by classical physics, providing no significant change in our understanding of reality.	f	\N
2136	506	The theories in quantum mechanics support the idea that reality operates solely on deterministic principles.	f	\N
2137	506	Quantum mechanics leads to practical benefits only, without affecting theoretical frameworks.	f	\N
2138	506	Quantum mechanics fundamentally alters our perception of reality by introducing concepts such as wave-particle duality and entanglement.	t	\N
2139	507	Maxwell's equations emphasize that electric currents cannot generate magnetic fields.	f	\N
2140	507	Maxwell's equations provide an argument that electricity and magnetism are completely independent phenomena.	f	\N
2141	507	Maxwell's equations describe how electric charges create electric fields.	t	\N
2142	507	Maxwell's equations state that electric fields do not influence magnetic fields.	f	\N
2143	508	The argument asserts that physical sciences operate independently of each other, thus emphasizing the uniqueness of each field.	f	\N
2144	508	The argument emphasizes that all physical phenomena are governed by strict deterministic laws, limiting the scope of scientific inquiry.	f	\N
2145	508	The argument highlights how advancements in one scientific field can lead to breakthroughs in others, demonstrating their mutual reliance.	t	\N
2146	508	The argument suggests that the complexities of climate change can be resolved through singular scientific approaches, reinforcing a limited perspective.	f	\N
2147	509	Single-discipline studies are deemed sufficient to tackle environmental issues on their own.	f	\N
2148	509	Interdisciplinary research is primarily motivated by funding opportunities rather than a genuine interest in scientific collaboration.	f	\N
2149	509	Interdisciplinary research is considered less important than traditional approaches focused solely on physical sciences.	f	\N
2150	509	Collaborative efforts among various scientific fields enhance the effectiveness of solutions to complex problems like climate change.	t	\N
2151	510	The laws of thermodynamics	f	\N
2152	510	The principle of superposition	f	\N
2153	510	The standard model of particle physics	f	\N
2154	510	Einstein's theory of relativity	t	\N
2155	511	To highlight the interconnectedness of various scientific principles and the importance of interdisciplinary research.	t	\N
2156	511	To argue that physical sciences are ultimately subjective and depend on individual interpretations.	f	\N
2157	511	To provide a detailed analysis of specific physical laws and their mathematical formulations.	f	\N
2158	511	To explain the historical developments in physical sciences and their impact on society.	f	\N
2159	512	Discrete sections highlighting individual historical figures.	f	\N
2160	512	Chronological order emphasizing the sequence of events.	t	\N
2161	512	Thematic organization focusing on technological advancements.	f	\N
2162	512	Comparative analysis linking different cultural effects.	f	\N
2163	513	The emphasis on humanism during the Renaissance encouraged scientific exploration.	t	\N
2164	513	The Renaissance stifled scientific innovation due to its focus on art.	f	\N
2165	513	The Renaissance had no significant impact on science according to the passage.	f	\N
2166	513	Scientific advancements were divorced from the intellectual climate of the Renaissance.	f	\N
2167	514	The spinning jenny	f	\N
2168	514	The mechanical clock	f	\N
2169	514	The steam engine	f	\N
2170	514	The printing press	t	\N
2171	515	To illustrate the interconnectedness of major historical events and their impacts on society.	t	\N
2172	515	To provide a detailed timeline of important inventions in history.	f	\N
2173	515	To highlight the negative consequences of exploration and industrialization.	f	\N
2174	515	To argue against the notion that art influences scientific progress.	f	\N
2175	516	Optimism	t	\N
2176	516	Pessimism	f	\N
2177	516	Social isolation	f	\N
2178	516	Cognitive inflexibility	f	\N
2179	517	The use of technology in psychology eliminates the need for human therapists.	f	\N
2180	517	Privacy concerns regarding digital tools are unfounded and negligible.	f	\N
2181	517	All digital mental health tools are considered effective and reliable.	f	\N
2182	517	Technology can improve access to mental health services for a wider audience.	t	\N
2183	518	Humanistic Therapy	f	\N
2184	518	Cognitive-Behavioral Therapy	t	\N
2185	518	Gestalt Therapy	f	\N
2186	518	Psychoanalysis	f	\N
2187	519	35, 15	t	A
2188	519	30, 12	f	B
2189	519	25, 10	f	C
2190	519	35, 20	f	A
2191	519	25, 15	t	B
2192	519	40, 5	f	C
2193	520	Yes, but it's close to the Operations department's ratio.	f	\N
2194	520	Yes, but it's close to the Operations department's ratio.	f	\N
2195	520	Yes, but it's close to the Operations department's ratio.	f	\N
2196	521	35	t	A
2197	521	30	f	B
2198	521	40	f	C
2199	521	10	t	A
2200	521	8	f	B
2201	521	12	f	C
2202	522	Product B	f	A
2203	522	Product A	t	B
2204	522	Product C	f	C
2205	522	200	t	A
2206	522	300	f	B
2207	522	100	f	C
2208	523	12000	f	A
2209	523	17500	t	B
2210	523	16500	f	C
2211	523	19000	f	A
2212	523	18000	f	B
2213	523	19500	t	C
2214	524	Automation will eliminate the need for a skilled workforce in logistics.	f	\N
2215	524	Job displacement is expected to be minimal with the integration of automation.	f	\N
2216	524	Companies should prioritize technology over workforce training to maximize efficiency.	f	\N
2217	524	A balanced approach requires investment in both technology and employee development.	t	\N
2218	524	All workforce impacts must be disregarded to focus on technology advancement.	f	\N
2219	525	Automation will eliminate the need for a skilled workforce in logistics.	f	\N
2220	525	Job displacement is expected to be minimal with the integration of automation.	f	\N
2221	525	Companies should prioritize technology over workforce training to maximize efficiency.	f	\N
2222	525	A balanced approach requires investment in both technology and employee development.	t	\N
2223	525	All workforce impacts must be disregarded to focus on technology advancement.	f	\N
2224	526	The West region has the highest market share.	f	\N
2225	526	The West region has the highest market share.	f	\N
2226	526	The West region has the highest market share.	f	\N
2227	527	5000	f	A
2228	527	9000	f	B
2229	527	7000	t	C
2230	527	20000	f	A
2231	527	15000	f	B
2232	527	30000	t	C
2233	528	5.0\\%, 8.0\\%	f	A
2234	528	4.7\\%, 7.0\\%	t	B
2235	528	4.5\\%, 6.5\\%	f	C
2236	528	5.5\\%, 7.5\\%	f	A
2237	528	4.0\\%, 6.0\\%	f	B
2238	528	3.5\\%, 5.0\\%	t	C
2239	529	50000	t	A
2240	529	45000	f	B
2241	529	55000	f	C
2242	529	42000	f	A
2243	529	38000	f	B
2244	529	40000	t	C
2245	530	The performance rating for the South region indicates its sales are acceptable.	f	\N
2246	530	The performance rating for the South region indicates its sales are acceptable.	f	\N
2247	530	The performance rating for the South region indicates its sales are acceptable.	f	\N
2248	531	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
2249	531	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
2250	531	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	f	\N
2251	531	EITHER statement ALONE is sufficient	f	\N
2252	531	Statements (1) and (2) TOGETHER are NOT sufficient	t	\N
2253	532	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
2254	532	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
2255	532	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	f	\N
2256	532	EITHER statement ALONE is sufficient	t	\N
2257	532	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
2258	533	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	t	\N
2259	533	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
2260	533	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	f	\N
2261	533	EITHER statement ALONE is sufficient	f	\N
2262	533	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
2263	534	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
2264	534	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
2265	534	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	t	\N
2266	534	EITHER statement ALONE is sufficient	f	\N
2267	534	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
2268	535	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
2269	535	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
2270	535	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	t	\N
2271	535	EITHER statement ALONE is sufficient	f	\N
2272	535	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
2273	536	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
3147	731	146 cartridges, 43800 pages	t	\N
2274	536	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
2275	536	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	t	\N
2276	536	EITHER statement ALONE is sufficient	f	\N
2277	536	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
2278	537	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
2279	537	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
2280	537	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	t	\N
2281	537	EITHER statement ALONE is sufficient	f	\N
2282	537	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
2283	538	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	t	\N
2284	538	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
2285	538	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	f	\N
2286	538	EITHER statement ALONE is sufficient	f	\N
2287	538	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
2288	539	Not Acceptable	f	\N
2289	539	Not Acceptable	f	\N
2290	540	No	f	\N
2291	540	No	f	\N
3148	731	140 cartridges, 42000 pages	f	\N
3149	732	2300.00	f	\N
3150	732	1500.00	f	\N
3151	732	2000.00	f	\N
3152	732	1800.00	t	\N
3153	733	10.70	f	\N
3154	733	10.50	t	\N
3155	733	10.10	f	\N
3156	733	0.50	f	\N
3157	734	k ≥ 10/x	f	\N
3158	734	k ≤ 10/x	t	\N
3159	734	k ≤ 10 + x	f	\N
3160	734	k < 10/x	f	\N
3161	735	270	t	\N
3162	735	255	f	\N
3163	735	240	f	\N
3164	735	252	f	\N
3165	736	26.0	f	\N
3166	736	8.0	f	\N
3167	736	21.0	f	\N
3168	736	16.0	t	\N
3169	737	1	t	\N
3170	737	2	f	\N
3171	737	3	f	\N
3172	737	0	f	\N
3173	738	$352,468.34	t	\N
3174	738	$362,468.34	f	\N
3175	738	$282,125.87	f	\N
3176	738	$332,468.34	f	\N
3177	739	$6	f	\N
3178	739	$6	f	\N
3179	739	$0	f	\N
3180	739	$8	t	\N
3181	740	24.0	f	\N
3182	740	20.0	f	\N
3183	740	30.0	t	\N
3184	740	36.0	f	\N
3185	741	$830.0	f	\N
3186	741	$648.0	f	\N
3187	741	$810.0	t	\N
3188	741	$760.0	f	\N
3189	742	0.4	f	\N
3190	742	0.5	t	\N
3191	742	1.0	f	\N
3192	742	0.75	f	\N
3193	743	57	f	\N
3194	743	48	f	\N
3195	743	51	f	\N
3196	743	54	t	\N
3197	744	3	f	\N
3198	744	4	f	\N
3199	744	2	t	\N
3200	744	1	f	\N
3201	745	2240.00	f	\N
3202	745	3440.00	f	\N
3203	745	2700.00	f	\N
3204	745	3740.00	f	\N
3205	745	3240.00	t	\N
3206	746	Tree Planting: $5000, Waste Management: $2000, Community Education: $3000	f	\N
3207	746	Tree Planting: $4000, Waste Management: $4000, Community Education: $2000	f	\N
3208	746	Tree Planting: $5000, Waste Management: $3000, Community Education: $1999	f	\N
3209	746	Tree Planting: $5000, Waste Management: $3000, Community Education: $2000	t	\N
3210	747	140	f	\N
3211	747	130	f	\N
3212	747	110	f	\N
3213	747	590	f	\N
3214	747	270	t	\N
3215	748	0	f	\N
3216	748	0	f	\N
3217	748	2	f	\N
3218	748	1	t	\N
3219	749	132	t	\N
3220	749	112	f	\N
3221	749	122	f	\N
3222	749	137	f	\N
3223	750	3	f	\N
3224	750	6	f	\N
3225	750	5	f	\N
3226	750	4	t	\N
3227	751	80	f	\N
3228	751	150	f	\N
3229	751	30	f	\N
3230	751	130	t	\N
3231	752	Communities can benefit from enhancing social engagement activities.	f	\N
3232	752	Social engagements are the only method to improve mental health.	f	\N
3233	752	Individuals with better mental health prefer fewer social interactions.	f	\N
3234	752	Mental health is influenced solely by external factors.	f	\N
3235	752	Stronger social connections correlate with lower stress levels.	t	\N
3236	753	The first statement is a premise, and the second is an assumption of the argument.	f	\N
3237	753	The first statement is an assumption, and the second is a premise supporting the argument.	f	\N
3238	753	Both statements are supporting premises that explain different aspects of fish population decline.	t	\N
3239	753	The first statement is a conclusion, and the second is a premise supporting that conclusion.	f	\N
3240	753	The first statement is a premise, and the second is a conclusion drawn from it.	f	\N
3241	754	Research shows that chronic stress can disrupt sleep cycles, impacting cognitive performance.	f	\N
3242	754	Athletes who adhered to strict sleep schedules demonstrated improved reaction times and decision-making.	t	\N
3243	754	Evidence suggests that a well-balanced diet can also enhance cognitive function independently of sleep.	f	\N
3244	754	A study found that individuals who sleep less than six hours a night are at a higher risk for memory issues.	f	\N
3245	754	Participants in a sleep experiment reported feeling more alert after a week of consistent sleep patterns.	f	\N
3246	755	Such plants do not require as much water as other species to thrive.	f	\N
3247	755	These plants may have higher rates of reproduction compared to non-resilient species.	f	\N
3248	755	These plants are likely to have developed adaptations that enhance their survival chances in diverse environments.	t	\N
3249	755	These plants have adaptations that are beneficial only in dry climates.	f	\N
3502	806	GMOs can lead to increased soil degradation over time.	f	\N
3503	807	Photosynthesis is a complex process that only certain plants can perform.	f	\N
3504	807	Photosynthesis is crucial for energy conversion and atmospheric balance.	t	\N
3505	807	Photosynthesis relies solely on water and sunlight to function effectively.	f	\N
3506	807	The process of photosynthesis primarily benefits animals rather than plants.	f	\N
3507	808	The geographical location of events	f	\N
3508	808	Cultural context and socio-economic factors	t	\N
3509	808	The number of battles fought during the era	f	\N
3510	808	Personal anecdotes of leaders involved	f	\N
3511	809	The Industrial Revolution led to changes solely in economic practices.	f	\N
3512	809	The Industrial Revolution primarily affected rural communities.	f	\N
3513	809	The Industrial Revolution was a period of social progress with no negative effects.	f	\N
3514	809	The Industrial Revolution resulted in significant economic and social transformations.	t	\N
3515	810	The fall of the Roman Empire was primarily due to external invasions.	f	\N
3516	810	Cultural, social, and economic factors are crucial to understanding historical events.	t	\N
3517	810	Historical events can be understood solely through military outcomes.	f	\N
3518	810	Historians always agree on the interpretation of historical events.	f	\N
3519	811	All countries experience the same outcomes from globalization.	f	\N
3520	811	Globalization exclusively benefits developed countries.	f	\N
3521	811	While globalization offers growth opportunities, it may also lead to increased inequality.	t	\N
3522	811	Economic development is unaffected by international trade.	f	\N
3523	812	Economic principles primarily concern personal finance management.	f	\N
3524	812	Globalization has no significant impact on economic theory.	f	\N
3525	812	Economic development only depends on technological advancements.	f	\N
3526	812	The interplay of micro and macroeconomic factors is essential for understanding economic behavior.	t	\N
3527	813	All economic actors seek to minimize their risks.	f	\N
3528	813	Individuals and firms are motivated primarily by altruism.	f	\N
3529	813	People respond predictably to changes in costs and benefits.	t	\N
3530	813	Economic behavior remains constant regardless of external factors.	f	\N
3531	814	The effects of natural resources on economic growth.	f	\N
3532	814	The role of government regulations in shaping market behavior.	f	\N
3533	814	The significance of understanding how economic principles apply to decision-making.	t	\N
3534	814	The importance of studying historical economic trends.	f	\N
3536	815	68.0	f	\N
3537	815	72.0	t	\N
3538	815	77.0	f	\N
3539	815	71.0	f	\N
3540	816	135	f	\N
3541	816	155	f	\N
3542	816	140	f	\N
3543	816	150	t	\N
3544	817	5.04	f	\N
3545	817	6.04	t	\N
3546	817	4.54	f	\N
3547	817	7.54	f	\N
3548	818	1000.0	f	\N
3549	818	900.0	f	\N
3550	818	940.0	f	\N
3551	818	954.5	t	\N
3552	819	11	f	\N
3553	819	8	f	\N
3554	819	10	t	\N
3555	819	13	f	\N
3556	820	50.0	f	\N
3557	820	70.0	f	\N
3558	820	75.0	f	\N
3559	820	60.0	t	\N
3560	821	5.31	f	\N
3561	821	-4.81	f	\N
3562	821	4.31	t	\N
3563	821	5	f	\N
3564	822	Employee Z is eligible when their score decreases to 40.	f	\N
3565	822	All employees are eligible due to a mistake in evaluation.	f	\N
3566	822	Employee X is eligible if their score is adjusted to be greater than 80.	t	\N
3567	822	Employee Y could be eligible if their score shifts to exactly 80.	f	\N
3568	823	-2085.00	f	\N
3569	823	-1285.00	f	\N
3570	823	215.00	f	\N
3571	823	-1785.00	t	\N
3572	824	$1977.50	f	\N
3573	824	$1777.50	t	\N
3574	824	$1877.50	f	\N
3575	824	$1677.50	f	\N
3576	825	$298.0 (from | using x=200 croissants & y=40 muffins) (False)	f	\N
3577	825	$294.0 (from | using x=120 croissants & y=120 muffins) (False)	f	\N
3578	825	$216 (from | using x=120 croissants & y=120 muffins) (Correct)	t	\N
3579	825	$297.0 (from | using x=180 croissants & y=60 muffins) (False)	f	\N
3580	826	-6	f	\N
3581	826	-5	f	\N
3582	826	-3	f	\N
3583	826	-4	t	\N
3584	827	75060.00	f	\N
3585	827	80460.00	t	\N
3586	827	80400.00	f	\N
3587	827	81460.00	f	\N
3588	828	$230.85	t	\N
3589	828	$230.85	t	\N
3590	828	$255.15	f	\N
3591	828	$245.85	f	\N
3592	829	$250.00	f	\N
3594	829	$320.00	f	\N
3595	829	$290.00	f	\N
3596	830	44434285.71	t	\N
3597	830	44435785.71	f	\N
3598	830	44432285.71	f	\N
3599	830	44430785.71	f	\N
3600	831	4 years	f	\N
3601	831	3 years	f	\N
3602	831	2 years	t	\N
3603	831	1 year	f	\N
3604	832	8000	f	\N
3605	832	10000	t	\N
3606	832	12000	f	\N
3607	832	15000	f	\N
3608	833	10	f	\N
3609	833	9	t	\N
3610	833	8	f	\N
3611	833	12	f	\N
3612	834	53	t	\N
3613	834	25	f	\N
3614	834	19	f	\N
3615	834	40	f	\N
3616	835	26	f	\N
3617	835	28	f	\N
3618	835	25	f	\N
3619	835	29	t	\N
3620	836	Increased microbial diversity will automatically increase crop prices.	f	\N
3621	836	This integration could ultimately reduce the environmental footprint of farming.	t	\N
3704	854	43.36	t	\N
3622	836	Investments in microbial research are necessary to understand the full benefits.	f	\N
3623	836	Most farmers are still resistant to adopting organic farming methods.	f	\N
3624	836	Farmers need to experiment with new crops to benefit from these practices.	f	\N
3625	837	greater employee retention and reduced hiring costs	t	\N
3626	837	a decrease in overall project completion times	f	\N
3627	837	less focus on innovation and creativity	f	\N
3628	837	increased customer complaints about service quality	f	\N
3629	837	more layoffs during economic downturns	f	\N
3630	838	The conclusion lacks evidence because it does not include examples of readers' interpretations of technology-themed novels.	f	\N
3631	838	The conclusion is sound as it highlights the tendency of literature to present one-dimensional narratives about technology.	f	\N
3632	838	The conclusion is well-supported as it acknowledges both the warnings and the limitations present in technology-themed literature.	t	\N
3633	838	The conclusion is weak since it ignores the possibility that readers can discern both positive and negative aspects of technology from such novels.	f	\N
3634	838	The conclusion is flawed because it fails to consider that literature can evolve to reflect the complexities of technology.	f	\N
3635	839	create confusion among employees regarding their roles.	f	\N
3636	839	eliminate the challenges of team collaboration.	f	\N
3637	839	reduce the need for office space altogether.	f	\N
3638	839	foster a more engaged and loyal workforce.	t	\N
3639	839	increase operational costs in the long term.	f	\N
3640	840	The relationship between creativity and happiness is independent of social relationships and physical health.	f	\N
3641	840	There may be other unconsidered factors that contribute to the reported happiness of individuals engaged in creative activities.	t	\N
3642	840	The survey conclusively proves that creativity is the sole factor contributing to happiness.	f	\N
3643	840	Engaging in creative activities always leads to increased happiness.	f	\N
3644	840	Individuals who are less happy tend to avoid creative activities.	f	\N
3645	841	It presents a counterargument to Professor Adams' assertion about classic literature.	t	\N
3646	841	It supports the idea that classic literature should be emphasized in education.	f	\N
3647	841	It introduces a new topic unrelated to the debate about classic literature.	f	\N
3648	841	It summarizes the main argument made by Professor Adams.	f	\N
3649	841	It offers a historical perspective on the relevance of diverse authors.	f	\N
3650	842	Established scholars always support emerging theories in their fields.	f	\N
3651	842	Some significant ideas are developed by those who are overlooked or marginalized.	t	\N
3652	842	Most revolutionary ideas are accepted immediately by their contemporaries.	f	\N
3653	842	Strong contributions often come from widely recognized figures in their time.	f	\N
3654	842	Cultural contexts have no impact on the acceptance of new ideas.	f	\N
3655	843	Antibiotic-resistant bacteria are a significant public health threat.	f	\N
3656	843	The mechanisms of antibiotic resistance are well understood.	f	\N
3657	843	Phages can be effectively isolated and characterized for therapeutic use.	t	\N
3658	843	Phage therapy will be more widely accepted than traditional antibiotics.	f	\N
3659	843	Phages are safer than all existing antibiotics.	f	\N
3660	844	Manipulating gut bacteria can lead to mental health improvements.	t	\N
3661	844	All gut bacteria impact mental health equally.	f	\N
3662	844	Current treatments for mental health are ineffective.	f	\N
3663	844	Mental health disorders are only caused by genetic factors.	f	\N
3664	844	Microbiomes are the only factor influencing mental health.	f	\N
3665	845	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
3666	845	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
3667	845	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	f	\N
3668	845	EITHER statement ALONE is sufficient	f	\N
3669	845	Statements (1) and (2) TOGETHER are NOT sufficient	t	\N
3670	846	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
3671	846	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
3672	846	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	f	\N
3673	846	EITHER statement ALONE is sufficient	f	\N
3674	846	Statements (1) and (2) TOGETHER are NOT sufficient	t	\N
3675	847	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
3676	847	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
3677	847	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	t	\N
3678	847	EITHER statement ALONE is sufficient	f	\N
3679	847	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
3680	849	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
3681	849	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
3682	849	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	f	\N
3683	849	EITHER statement ALONE is sufficient	f	\N
3684	849	Statements (1) and (2) TOGETHER are NOT sufficient	t	\N
3685	850	14400	t	\N
3686	850	2880	f	\N
3687	850	14534	f	\N
3688	850	13722	f	\N
3689	850	11417	f	\N
3690	851	x = 0	t	\N
3691	851	x = -1/((-1296 + 3*sqrt(186621))**(1/3)*(-1/2 - sqrt(3)*I/2) + 1)	f	\N
3692	851	x = -3/((-1296 + 3*sqrt(186621))**(1/3)*(-1/2 - sqrt(3)*I/2))	f	\N
3693	851	x = -1/((-1296 + 3*sqrt(186621))**(1/3)*(-1/2 - sqrt(3)*I/2)) - (-1296 + 3*sqrt(186621))**(1/3)*(-1/2 - sqrt(3)*I/2)/3	t	\N
3694	852	16500.00	t	\N
3695	852	17000.00	f	\N
3696	852	15750.00	f	\N
3697	852	17250.00	f	\N
3698	853	65000.00	f	\N
3699	853	60000.00	t	\N
3700	853	55000.00	f	\N
3701	853	60000.00	t	\N
3702	854	50.26	f	\N
3703	854	32.94	f	\N
3705	854	31.21	f	\N
3706	855	46.27	f	\N
3707	855	31.19	f	\N
3708	855	35.79	t	\N
3709	855	24.03	f	\N
3710	856	44.14	f	\N
3711	856	34.13	t	\N
3712	856	31.66	f	\N
3713	856	25.36	f	\N
3714	857	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
3715	857	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
3716	857	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	t	\N
3717	857	EITHER statement ALONE is sufficient	f	\N
3718	857	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
3719	859	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
3720	859	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
3721	859	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	t	\N
3722	859	EITHER statement ALONE is sufficient	f	\N
3723	859	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
3724	860	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
3725	860	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
3726	860	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	f	\N
3727	860	EITHER statement ALONE is sufficient	f	\N
3728	860	Statements (1) and (2) TOGETHER are NOT sufficient	t	\N
3729	861	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
3730	861	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
3731	861	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	t	\N
3732	861	EITHER statement ALONE is sufficient	f	\N
3733	861	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
3734	862	Total work completed is 1.1 of the tower.	t	\N
3735	862	Total work completed is 1.00 of the tower.	f	\N
3736	862	Total work completed is 0.85 of the tower.	f	\N
3737	862	Total work completed is 0.90 of the tower.	f	\N
3738	864	258.75 Tulips still needed	f	\N
3739	864	368.75 Tulips still needed	f	\N
3740	864	218.75 Tulips still needed	f	\N
3741	864	-78.75 Tulips still needed	t	\N
3742	865	12500	f	\N
3743	865	16000	f	\N
3744	865	12500	f	\N
3745	865	13500	t	\N
3746	866	15600	f	\N
3747	866	9000	t	\N
3748	866	8000	f	\N
3749	866	8000	f	\N
3750	867	150%	f	\N
3751	867	30.77%	t	\N
3752	867	16.67%	f	\N
3753	867	20%	f	\N
3754	868	-20%	f	\N
3755	868	11.11%	f	\N
3756	868	30%	f	\N
3757	868	10%	t	\N
3758	869	175 billion USD for retail and 175 billion USD for healthcare	f	\N
3759	869	140 billion USD for retail and 175 billion USD for healthcare	t	\N
3760	869	105 billion USD for retail and 210 billion USD for healthcare	f	\N
3761	869	140 billion USD for retail and 140 billion USD for healthcare	f	\N
3762	870	244 billion USD for finance and 54 billion USD for manufacturing	f	\N
3763	870	244 billion USD for finance and 70 billion USD for manufacturing	t	\N
3764	870	280 billion USD for finance and 54 billion USD for manufacturing	f	\N
3765	870	210 billion USD for finance and 89 billion USD for manufacturing	f	\N
3766	871	Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient	f	\N
3767	871	Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient	f	\N
3768	871	BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient	t	\N
3769	871	EITHER statement ALONE is sufficient	f	\N
3770	871	Statements (1) and (2) TOGETHER are NOT sufficient	f	\N
3771	872	apathy	f	\N
3772	872	clarity	f	\N
3773	872	confusion	t	\N
3774	872	tranquility	f	\N
3775	872	solitude	f	\N
3776	872	excitement	f	\N
3777	873	concrete	f	A
3778	873	abstract	t	B
3779	873	theoretical	f	C
3780	873	substantial	f	D
3781	873	mythical	f	A
3782	873	speculative	f	B
3783	873	practical	t	C
3784	873	empirical	f	D
3785	874	acute	t	\N
3786	874	dull	f	\N
3787	874	keen	t	\N
3788	874	irresolute	f	\N
3789	874	overstated	f	\N
3790	874	neutral	f	\N
3791	875	despair	f	\N
3792	875	apathy	f	\N
3793	875	cynicism	t	\N
3794	875	disappointment	f	\N
3795	875	enthusiasm	t	\N
3796	875	optimism	f	\N
3797	876	recognition	f	A
3798	876	abandonment	f	B
3799	876	celebration	t	C
3800	876	denial	f	D
3801	876	illustration	f	A
3802	876	revelation	t	B
3803	876	exaltation	f	C
3804	876	exploration	f	D
3805	876	elevation	f	A
3806	876	failure	t	B
3807	876	ascendance	f	C
3808	876	redemption	f	D
3809	877	Understanding atmospheric pressure is irrelevant to weather predictions.	f	\N
3810	877	High-pressure systems always lead to stormy weather.	f	\N
3811	877	Low-pressure zones are typically associated with clear weather.	f	\N
3812	877	Changes in atmospheric pressure can affect local ecosystems.	t	\N
3813	878	Ethical debates surrounding genetic modification highlight the need for responsible research.	t	\N
3814	878	There is a consensus among scientists that genetic engineering should proceed without regulation.	f	\N
3815	878	The benefits of genetic engineering are universally agreed upon by all stakeholders.	f	\N
3816	878	Genetic engineering poses no ethical concerns in agriculture.	f	\N
3817	879	The principles of classical physics can fully explain quantum mechanics.	f	\N
3818	879	Quantum entanglement only occurs in experimental settings.	f	\N
3819	879	Utilizing quantum entanglement can enhance computational power and security.	t	\N
3820	879	Entangled particles can communicate information faster than light.	f	\N
3821	880	Only fiscal policy is essential for managing economic performance.	f	\N
3822	880	Monetary policy has no significant impact on employment levels.	f	\N
3823	880	Monetary and fiscal policies are ineffective in achieving economic stability.	f	\N
3824	880	Both policies aim to balance immediate economic needs with long-term stability.	t	\N
3825	881	Policymakers will need to integrate behavioral insights to address modern economic issues.	t	\N
3826	881	The emphasis on protective trade measures will dominate future economic policies.	f	\N
3827	881	Fiscal and monetary policies will become irrelevant as economies evolve.	f	\N
3828	881	Economic policymaking will increasingly rely on traditional methods without adapting to new challenges.	f	\N
3829	882	Policies based on behavioral insights can lead to more effective economic outcomes.	t	\N
3830	882	Economic models are sufficient to predict human behavior accurately.	f	\N
3831	882	Individuals always make rational economic decisions.	f	\N
3832	882	Government intervention is unnecessary in a fully competitive market.	f	\N
3833	883	Global economic factors have minimal impact on national policies.	f	\N
3834	883	Behavioral insights are irrelevant to the effectiveness of economic policies.	f	\N
3835	883	The synergy between monetary and fiscal policies is essential for economic stability.	t	\N
3836	883	Economic policies operate independently of one another.	f	\N
3837	884	uncontested	f	\N
3838	884	simple	f	\N
3839	884	resolute	f	\N
3840	884	trivial	f	\N
3841	884	ordinary	f	\N
3842	884	enigmatic	t	\N
3843	885	augment	t	A
3844	885	incite	f	B
3845	885	curtail	f	C
3846	885	dwindle	f	D
3847	885	escalate	f	A
3848	885	ameliorate	f	B
3849	885	exacerbate	f	C
3850	885	mitigate	t	D
3851	886	predictable	f	\N
3852	886	mundane	f	\N
3853	886	conventional	f	\N
3854	886	trivial	f	\N
3855	886	benign	f	\N
3856	886	anomalous	t	\N
3857	887	multidimensional	t	A
3858	887	stereotypical	f	B
3859	887	superficial	f	C
3860	887	ordinary	f	D
3861	887	forget	f	A
3862	887	observe	f	B
3863	887	ignore	f	C
3864	887	experience	t	D
3865	887	richness	t	A
3866	887	hollowness	f	B
3867	887	triviality	f	C
3868	887	banality	f	D
3869	888	similar	f	\N
3870	888	intertwined	t	\N
3871	888	independent	f	\N
3872	888	contradictory	f	\N
3873	888	irrelevant	f	\N
3874	888	complementary	t	\N
3875	889	stability	f	A
3876	889	innovation	f	B
3877	889	protectionism	t	C
3878	889	liberation	f	D
3879	889	inequality	f	A
3880	889	efficiency	f	B
3881	889	redistribution	f	C
3882	889	growth	t	D
3883	889	intervention	f	A
3884	889	reduction	f	B
3885	889	regulation	t	C
3886	889	development	f	D
3887	890	It provides diverse perspectives that lead to more holistic solutions.	t	\N
3888	890	It promotes the idea that all philosophical problems have a definitive answer.	f	\N
3889	890	It simplifies complex issues by removing philosophical jargon.	f	\N
3890	890	It encourages philosophers to solely focus on abstract theories.	f	\N
3891	891	Philosophical discussions about free will are becoming irrelevant due to neuroscience.	f	\N
3892	891	Neuroscience definitively proves that humans lack free will.	f	\N
3893	891	The findings of neuroscience challenge traditional notions of autonomy.	t	\N
3894	891	Neuroscience supports the idea that all decisions are made consciously.	f	\N
3895	892	The Renaissance occurred in a vacuum, separate from political changes.	f	\N
3896	892	The Renaissance artists were primarily focused on traditional religious themes.	f	\N
3897	892	The advancements made during the Renaissance had lasting effects on various aspects of society.	t	\N
3898	892	Literacy rates did not improve during the Renaissance.	f	\N
3899	893	The Industrial Revolution did not change demographic patterns.	f	\N
3900	893	Urbanization was a response to the demand for labor in factories.	t	\N
3901	893	The rise of factories had no effect on population distribution.	f	\N
3902	893	Urbanization led to improvements in rural living conditions.	f	\N
3903	894	The revolution primarily benefited only the elite class.	f	\N
3904	894	The American Revolution had no influence on other nations seeking independence.	f	\N
3905	894	The American colonies were unified in their desire for independence.	t	\N
3906	894	The principles of equality were already prevalent in societies worldwide.	f	\N
3907	895	Public distrust in scientific studies has led to a rise in pseudoscience.	f	\N
3908	895	Scientific advancements often lead to ethical dilemmas that challenge their societal acceptance.	f	\N
3909	895	Interdisciplinary approaches often yield solutions that do not rely solely on scientific methods.	f	\N
3910	895	Many traditional practices, such as herbal medicine, have shown effectiveness without scientific validation.	t	\N
3911	896	Scientists rely solely on peer review to verify their findings before public dissemination.	f	\N
3912	896	Peer review is unnecessary for research that has already demonstrated its validity.	f	\N
3913	896	The peer review process often delays the publication of groundbreaking research.	f	\N
3914	896	Peer review serves to enhance the credibility and quality of scientific research.	t	\N
3915	897	Scientific literacy is not dependent on factors outside formal education.	f	\N
3916	897	Science is a universally understood language that transcends cultural differences.	f	\N
3917	897	Students who receive science education are more likely to engage with scientific topics in adulthood.	t	\N
3918	897	The current educational system effectively promotes critical thinking in every subject.	f	\N
3919	898	Understanding science requires a basic education, which is universally accessible to everyone.	f	\N
3920	898	Ethical dilemmas often overshadow the positive contributions of scientific advancements.	f	\N
3921	898	Science is an essential component of societal progress and addresses complex global challenges.	t	\N
3922	898	The scientific method is often disregarded in traditional practices that yield effective results.	f	\N
3593	829	$300.00	t	\N
\.


--
-- Data for Name: problems; Type: TABLE DATA; Schema: public; Owner: compexe_admin
--

COPY public.problems (type, prompt, problemid, sectionid, examtypeid, title, text, difficulty, correctattemptscount, totalattemptscount, metadata, creationdate, "addedDate", "isChildren", "problemsSetId", mocksectionid, "isMockQuestion", solution, mockquestionnumber) FROM stdin;
MCQ-Single	<Real Contextual> - <Algebra> - <Backsolving> - <Algebraic Equations> - <difficulty_level: 1>	541	3	2	Chocolate Cake Sales in Quantopia Bakery	In a recent survey conducted in the small town of Quantopia, the local bakery reported that the number of chocolate cakes sold in the morning is equal to twice the number of vanilla cakes sold. If the bakery sold a total of 30 cakes in the morning, how many chocolate cakes did they sell?	1	0	0	{}	2025-02-07 06:46:50.224	2025-02-07 06:46:50.224	f	\N	\N	f	{"solution": "<p>Let:</p>\\n<p>x = \\\\text{number of vanilla cakes sold}</p>\\n<p>Then, the number of chocolate cakes sold = 2x.</p>\\n<p>We can write the equation:</p>\\n<p>x + 2x = 30</p>\\n<p>3x = 30</p>\\n<p>x = \\\\frac{30}{3} = 10</p>\\n<p>Thus, the number of chocolate cakes sold is:</p>\\n<p>2x = 2 \\\\times 10 = 20</p>\\n<p>Therefore, the bakery sold 20 chocolate cakes in the morning.</p>"}	\N
MCQ-Single	<Real Contextual> - <Word Problems> - <Assessing given Situation(checking the ability of accessing a given situation)> - <Percentages> - <Accounting> - <difficulty_level: 1>	542	3	2	Calculating Savings from Seasonal Discounts at a Local Bakery	In a quaint little town, a local bakery known for its delicious pastries has decided to offer a seasonal discount of 20\\% on all items to attract customers. If a customer purchases a dozen croissants priced at \\$5 each, how much money does the customer save due to the discount? Calculate the total cost of the croissants before and after applying the discount to determine the savings. What is the total amount saved?	1	0	0	{}	2025-02-07 06:46:50.263	2025-02-07 06:46:50.263	f	\N	\N	f	{"solution": "<p>The total cost of the croissants before discount is calculated as follows:</p> <p>~~\\\\text{Total Cost Before Discount} = \\\\text{Price Per Croissant} \\\\times \\\\text{Number of Croissants} = 5 \\\\times 12 = 60\\\\$~~</p> <p>The total discount applied is:</p> <p>~~\\\\text{Total Discount} = \\\\text{Total Cost Before Discount} \\\\times \\\\text{Discount Rate} = 60 \\\\times 0.20 = 12\\\\$~~</p> <p>The total cost after applying the discount becomes:</p> <p>~~\\\\text{Total Cost After Discount} = \\\\text{Total Cost Before Discount} - \\\\text{Total Discount} = 60 - 12 = 48\\\\$~~</p> <p>Thus, the total amount saved by the customer is \\\\$12.</p>"}	\N
MCQ-Single	<Pure Contextual> - <Arithmetic> - <Number Sense> - <Work and Time> - <difficulty_level: 2>	543	3	2	Community Fountain Construction: Work and Time Calculation	In a quaint village, a group of enthusiastic villagers decided to work together to build a community fountain. They estimated that the total work required to complete the fountain would take 120 hours if they all worked together continuously. However, due to unforeseen circumstances, only 6 villagers were available to work each day for the first two days. Each villager is capable of completing 1/120 of the work in one hour. After two days, 4 additional villagers joined, increasing their total number to 10. Assuming that all the villagers are equally efficient, how many more days will it take for the whole group of 10 to finish the remaining work? Please calculate the total time taken to complete the fountain in hours and then convert this into days. Note that it may require a few steps of calculation to arrive at the total number of days needed.	2	0	0	{}	2025-02-07 06:46:50.292	2025-02-07 06:46:50.292	f	\N	\N	f	{"solution": "<p>To find the solution, we begin by calculating the amount of work done by the initial group of villagers:</p>\\n\\n<p>1. Initially, 6 villagers work for 2 days (which is 48 hours) as follows:</p>\\n<p>Work done by 6 villagers = 6 \\\\times \\\\frac{1}{120} \\\\times (6 \\\\times 24) = 6 \\\\times \\\\frac{1}{120} \\\\times 48 = \\\\frac{288}{120} = 2.4\\\\ hours</p>\\n\\n<p>2. Next, we calculate the remaining work after the first 2 days:</p>\\n<p>Remaining work = 120 - 2.4 = 117.6\\\\ hours</p>\\n\\n<p>3. After the first 2 days, 4 more villagers join, making a total of 10 villagers. Therefore, the work done by 10 villagers per hour is:</p>\\n<p>Work done by 10 villagers = 10 \\\\times \\\\frac{1}{120} = \\\\frac{10}{120} = \\\\frac{1}{12}\\\\ hours.</p>\\n\\n<p>4. Now we calculate the time needed to complete the remaining work with 10 villagers:</p>\\n<p>Time to complete remaining work = \\\\frac{117.6}{\\\\frac{1}{12}} = 117.6 \\\\times 12 = 1411.2\\\\ hours</p>\\n\\n<p>5. Finally, we convert this time from hours into days:</p>\\n<p>Total days needed = \\\\frac{1411.2}{24} \\\\approx 58.80 days.</p>\\n\\n<p>Thus, it will take approximately 58.80 days for the villagers to complete the fountain.</p>"}	\N
MCQ-Single	<Pure Contextual> - <Word Problems> - <Setting up proper steps(questions that require users to properly setting up the steps to solve the questions)> - <Work and Time> - <Taxation> - <difficulty_level: 1>	544	3	2	Work Efficiency of Bakers in a Busy Day	In a quaint little town, a local bakery employs two bakers, Alice and Bob, who together have the ability to produce a batch of delicious pastries in 6 hours. However, Alice is known to be slightly faster; she can complete the same batch alone in 4 hours, while Bob, on the other hand, takes 12 hours. Given this context, if both bakers decide to work together on a busy Saturday, and they manage to produce an extra 3 batches within the duration of a single Saturday, how long did they take to make these extra batches during their busy working period?	1	0	0	{}	2025-02-07 06:46:50.323	2025-02-07 06:46:50.323	f	\N	\N	f	{"solution": "First, we calculate the work rates of Alice and Bob:<br>- Alice's work rate: ~~\\\\frac{1 \\\\text{ batch}}{4 \\\\text{ hours}} = 0.25 \\\\text{ batches per hour}~~<br>- Bob's work rate: ~~\\\\frac{1 \\\\text{ batch}}{12 \\\\text{ hours}} = 0.0833 \\\\text{ batches per hour}~~<br><br>Now, to find their combined work rate:<br>Combined work rate = ~~0.25 + 0.0833 = 0.3333 \\\\text{ batches per hour}~~<br><br>Next, we need to calculate the time taken to produce 3 batches:<br>Let \\\\( t \\\\) be the time in hours to produce 3 batches.<br>Thus, we have:<br><br>~~t \\\\times 0.3333 = 3~~<br><br>Solving for \\\\( t \\\\):<br>~~t = \\\\frac{3}{0.3333} \\\\approx 9 \\\\text{ hours}~~<br><br>Therefore, Alice and Bob took approximately 9 hours to make the extra 3 batches on that busy Saturday."}	\N
MCQ-Single	<Real Contextual> - <Arithmetic> - <common pitfalls> - <Percentages> - <difficulty_level: 3>	545	3	2	Calculating the Total Cost of Balloons with Discounts and Taxes	In a vibrant city fair, a booth sells colorful balloons at a fixed price. During the fair, the vendor decides to offer a promotional discount of 25% on all balloon purchases. If a shopper buys a total of 10 balloons, the original price per balloon is \\$4. After the discount, the shopper also encounters an unexpected 10% sales tax on the final price. What is the total amount the shopper spends on these 10 balloons after applying the discount and adding the sales tax? Be careful with the calculations, as rounding at different stages may lead to different outcomes.	3	0	0	{}	2025-02-07 06:46:50.351	2025-02-07 06:46:50.351	f	\N	\N	f	{"solution": "<html><p>To determine the total amount spent by the shopper on the balloons, we will follow these steps:</p><ol><li>Calculate the total original price of the balloons:</li> <p>\\\\( \\\\text{Total Original Price} = \\\\text{Price per Balloon} \\\\times \\\\text{Number of Balloons} = 4.00 \\\\times 10 = 40.00 \\\\, \\\\text{USD} \\\\)</p> <li>Calculate the discount amount:</li> <p>\\\\( \\\\text{Discount Amount} = \\\\text{Total Original Price} \\\\times \\\\text{Discount Percentage} = 40.00 \\\\times 0.25 = 10.00 \\\\, \\\\text{USD} \\\\)</p> <li>Calculate the price after discount:</li> <p>\\\\( \\\\text{Price After Discount} = \\\\text{Total Original Price} - \\\\text{Discount Amount} = 40.00 - 10.00 = 30.00 \\\\, \\\\text{USD} \\\\)</p> <li>Calculate the sales tax amount:</li> <p>\\\\( \\\\text{Sales Tax Amount} = \\\\text{Price After Discount} \\\\times \\\\text{Sales Tax Percentage} = 30.00 \\\\times 0.10 = 3.00 \\\\, \\\\text{USD} \\\\)</p> <li>Calculate the final price after tax:</li> <p>\\\\( \\\\text{Final Price} = \\\\text{Price After Discount} + \\\\text{Sales Tax Amount} = 30.00 + 3.00 = 33.00 \\\\, \\\\text{USD} \\\\)</p></ol><p>Thus, the total amount spent by the shopper on the balloons after applying the discount and adding the sales tax is \\\\$33.00.</p></html>"}	\N
MCQ-Single	<Pure Contextual> - <Algebra> - <Backsolving> - <Functions> - <difficulty_level: 1>	546	3	2	Finding the Total Cost of Lattes at a Quirky Café	A quirky café is known for serving unique flavored lattes. The café offers three sizes of lattes - small, medium, and large. If the price of a small latte is represented by \\( x \\), the medium latte costs \\( 1.5x \\), and the large latte costs \\( 2.2x \\). If a customer orders one small, one medium, and one large latte, what is the total cost in terms of \\( x \\)?	1	0	0	{}	2025-02-07 06:46:50.37	2025-02-07 06:46:50.37	f	\N	\N	f	{"solution": "To find the total cost of the lattes in terms of \\\\( x \\\\), we can calculate as follows:<br><br>1. The cost of a small latte is \\\\( x \\\\).<br>2. The cost of a medium latte is \\\\( 1.5x \\\\).<br>3. The cost of a large latte is \\\\( 2.2x \\\\).<br><br>Now, the total cost can be expressed as:<br>\\\\[ \\\\text{Total Cost} = x + 1.5x + 2.2x \\\\]<br>\\\\[ \\\\text{Total Cost} = (1 + 1.5 + 2.2)x \\\\]<br>\\\\[ \\\\text{Total Cost} = 4.7x \\\\]<br><br>Thus, the total cost of one small, one medium, and one large latte is \\\\( 4.7x \\\\)."}	\N
MCQ-Single	<Real Contextual> - <Word Problems> - <Setting up proper steps(questions that require users to properly setting up the steps to solve the questions)> - <Inequalities> - <Accounting> - <difficulty_level: 1>	547	3	2	Inequalities in Profit Management: An Accounting Dilemma	In a small accounting firm, Sarah is tasked with managing the financial records for two different clients, Client A and Client B. Client A's records are expected to generate a profit of at least \\$1,500, while Client B's records should yield a profit of at least \\$1,200. If Sarah's total profit from both clients cannot exceed \\$3,000 due to budget constraints set by her firm, which of the following inequalities represents the situation described? Let x represent the profit from Client A and y represent the profit from Client B.	1	0	0	{}	2025-02-07 06:46:50.398	2025-02-07 06:46:50.398	f	\N	\N	f	{"solution": "The situation can be represented by the following inequalities:<ul><li>\\\\( x \\\\geq 1500 \\\\) - Profit from Client A</li><li>\\\\( y \\\\geq 1200 \\\\) - Profit from Client B</li><li>\\\\( x + y \\\\leq 3000 \\\\) - Total profit constraint</li></ul>These inequalities reflect the requirements of profit generation set for Sarah in the accounting firm."}	\N
MCQ-Single	<Real Contextual> - <Word Problems> - <Mathematical tools(Questions which may have 2 or more mathematical approachs to solve, but user would have to choose the most optimal and efficient approach: generate question content in that manner)> - <Polynomials> - <Strategy and Management> - <difficulty_level: 4>	548	3	2	Optimizing Resource Allocation for Project Efficiency in Strategic Management	In a recent evaluation of a strategic management initiative aimed at enhancing project efficiency, a company's project manager devised a polynomial model representing the relationship between the number of resources allocated (x) and the completion time (y) in days for a specific project. The polynomial is defined as y = 3x^2 - 12x + 18, where x must be a positive integer. The management wants to assess the completion time as resources are adjusted, noting that they aim for a completion time no greater than 30 days. Considering the constraints involved in resource allocation, the project manager sets aside a budget allowing for the deployment of up to 8 resources. However, they also receive feedback from team members suggesting that employing a reduction strategy by redistributing existing resources could optimize completion time without exceeding the set budget. Based on this, what is the maximum number of resources that can be allocated while still ensuring the project is completed in accordance with the stipulated timeframe of 30 days?	4	0	0	{}	2025-02-07 06:46:50.432	2025-02-07 06:46:50.432	f	\N	\N	f	{"solution": "<p>To solve the problem, we start by setting the polynomial equal to 30, since we want to find when the project can be completed in at most 30 days:</p> <p>~~y = 3x^{2} - 12x + 18 = 30~~</p> <p>Rearranging gives:</p> <p>~~3x^{2} - 12x + 18 - 30 = 0~~</p> <p>Which simplifies to:</p> <p>~~3x^{2} - 12x - 12 = 0~~</p> <p>Now, we can factor or use the quadratic formula:</p> <p>Using the quadratic formula: ~~x = \\\\frac{-b \\\\pm \\\\sqrt{b^{2} - 4ac}}{2a}~~</p> <p>Where:\\n - a = 3\\n - b = -12\\n - c = -12</p> <p>Calculating the discriminant:</p> <p>~~b^{2} - 4ac = (-12)^{2} - 4(3)(-12) = 144 + 144 = 288~~</p> <p>Now applying the quadratic formula:</p> <p>~~x = \\\\frac{12 \\\\pm \\\\sqrt{288}}{6}~~</p> <p>This gives two possible solutions. However, since we are interested in positive integer values of x, we only consider those solutions which are greater than zero. Solving further:</p> <p>After calculating, the relevant solution for x that aligns with the conditions of resource allocation is approximately: ~~x \\\\approx 4.83~~</p> <p>Since x must be a positive integer, we take the maximum possible integer value, thus:</p> <p>The maximum number of resources that can be allocated while ensuring project completion within 30 days is: <strong>5</strong>.</p>"}	\N
MCQ-Single	<Pure Contextual> - <Algebra> - <Number Picking(by logical and critical reasoning over constraints given in the question)> - <Polynomials> - <difficulty_level: 5>	549	3	2	Polynomial Evaluation in a Competitive Scenario	In a mathematical competition, participants were tasked with solving a complex polynomial equation defined as -5x^2 + -8x + 5y + -2. The evaluators noticed that the first variable, x, is greatly affected by the value of y. To streamline the grading, it was determined that when x is set to 5, the total value of the polynomial must yield a sum close to -40. Only the candidates who can critically evaluate the function and correctly deduce the other values will pass. Which of the following values of y would allow the polynomial to satisfy the condition stated by the evaluators?	5	0	0	{}	2025-02-07 06:46:50.46	2025-02-07 06:46:50.46	f	\N	\N	f	{"solution": "<p>To determine the value of y that satisfies the polynomial equation, we start with the given values:</p> <p>Let \\\\( x = 5 \\\\) and we want the polynomial to sum up to \\\\( -40 \\\\).</p> <p>Substituting \\\\( x \\\\) into the polynomial:</p> <p>\\\\( -5x^{2} + -8x + 5y + -2 = -40 \\\\)</p> <p>This simplifies to:</p> <p>\\\\( -5(5)^{2} + -8(5) + 5y + -2 = -40 \\\\)</p> <p>Calculating the left-hand side:</p> <p>\\\\( -5(25) + -40 + 5y - 2 = -40 \\\\)</p> <p>Which simplifies to:</p> <p>\\\\( -125 + 5y - 2 = -40 \\\\)</p> <p>Now, combining the constants:</p> <p>\\\\( 5y - 127 = -40 \\\\)</p> <p>Adding 127 to both sides gives:</p> <p>\\\\( 5y = 87 \\\\)</p> <p>Dividing both sides by 5 yields:</p> <p>\\\\( y = \\\\frac{87}{5} = 17.4 \\\\)</p><p>Thus, the value of y that would allow the polynomial to satisfy the evaluators' condition is:</p> <p>\\\\( y = 17.4 \\\\)</p>"}	\N
MCQ-Single	<Real Contextual> - <Arithmetic> - <Critical Reasoning> - <Unitary Method> - <difficulty_level: 1>	550	3	2	Flour Calculation for Bread Production in a Bakery	In a small bakery, the baker uses 2 kg of flour to make 16 loaves of bread. If she wants to make 48 loaves, how much flour does she need to use? A helpful tip: think about how much flour is used for each loaf and then scale it accordingly.	1	0	0	{}	2025-02-07 06:46:50.488	2025-02-07 06:46:50.488	f	\N	\N	f	{"solution": "To determine the amount of flour required for 48 loaves, we first find out how much flour is used for one loaf.<br><br>1. Calculate flour per loaf:<br>   \\\\text{Flour per loaf} = \\\\frac{2 \\\\text{ kg}}{16 \\\\text{ loaves}} = 0.125 \\\\text{ kg per loaf}<br><br>2. Now, to find the flour needed for 48 loaves:<br>   \\\\text{Total flour for 48 loaves} = 0.125 \\\\text{ kg/loaf} \\\\times 48 \\\\text{ loaves} = 6.0 \\\\text{ kg}<br><br>Thus, the total amount of flour required to produce 48 loaves of bread is 6.0 kg."}	\N
MCQ-Single	<Pure Contextual> - <Algebra> - <Number Picking(by logical and critical reasoning over constraints given in the question)> - <Polynomials> - <difficulty_level: 2>	551	3	2	Maximizing Flowers Planted in a Community Garden Using a Polynomial Model	A local gardening club has decided to plant a new type of flower in their community garden. They have created a polynomial equation to model the number of flowers (f) they can plant based on the number of garden beds (b). The equation is given by f(b) = -1b^3 + 4b^2 + 1b + -4. The club currently has 4 garden beds available for planting. If they want to maximize the number of flowers planted while still staying within the positive integer quantity of flowers, what is the maximum number of flowers they can plant using their polynomial equation? Choose the appropriate number of garden beds they should use from the options provided.	2	0	0	{}	2025-02-07 06:46:50.524	2025-02-07 06:46:50.524	f	\N	\N	f	{"solution": "<h3>Solution:</h3> <p>To find the maximum number of flowers that can be planted using the polynomial equation <strong>f(b) = -1b^3 + 4b^2 + 1b - 4</strong>, we evaluate this polynomial for the integer values of garden beds (b) from 1 to 4:</p> <ul> <li>For b = 1: f(1) = -1(1^3) + 4(1^2) + 1(1) - 4 = 0</li> <li>For b = 2: f(2) = -1(2^3) + 4(2^2) + 1(2) - 4 = 6</li> <li>For b = 3: f(3) = -1(3^3) + 4(3^2) + 1(3) - 4 = 8</li> <li>For b = 4: f(4) = -1(4^3) + 4(4^2) + 1(4) - 4 = 0</li> </ul> <p>Thus, the maximum number of flowers that can be planted using 3 garden beds is <strong>8</strong>.</p>"}	\N
MCQ-Single	<Real Contextual> - <Word Problems> - <Assessing given Situation(checking the ability of accessing a given situation)> - <Polynomials> - <Taxation> - <difficulty_level: 1>	552	3	2	Calculating Tax Liability for a Small Business Based on Employee Count	In a bustling city, a government official proposed a new tax policy affecting the city's residents. The tax on small businesses is represented by the polynomial expression \\( P(x) = 2x^{2} + 3x + 5 \\), where \\( x \\) represents the number of employees in a small business. If a business has 3 employees, how much tax would the business owe? Calculate the tax using the polynomial provided and determine the total tax liability for a small business with 3 employees.	1	0	0	{}	2025-02-07 06:46:50.565	2025-02-07 06:46:50.565	f	\N	\N	f	{"solution": "To find the tax owed by a business with 3 employees, we will use the polynomial \\\\( P(x) = 2x^{2} + 3x + 5 \\\\). We will evaluate this polynomial at \\\\( x = 3 \\\\):<br><br>1. Substitute \\\\( x \\\\) into the polynomial:<br>   \\\\( P(3) = 2(3)^{2} + 3(3) + 5 \\\\)<br>2. Calculate \\\\( (3)^{2} = 9 \\\\):<br>   \\\\( P(3) = 2(9) + 3(3) + 5 \\\\)<br>3. Multiply: \\\\( 2(9) = 18 \\\\)<br>   \\\\( P(3) = 18 + 3(3) + 5 \\\\)<br>4. Calculate \\\\( 3(3) = 9 \\\\):<br>   \\\\( P(3) = 18 + 9 + 5 \\\\)<br>5. Add all terms: \\\\( P(3) = 18 + 9 + 5 = 32 \\\\)<br><br>Thus, the total tax liability for a small business with 3 employees is \\\\$ 32."}	\N
MCQ-Single	<Pure Contextual> - <Word Problems> - <Mathematical tools(Questions which may have 2 or more mathematical approachs to solve, but user would have to choose the most optimal and efficient approach: generate question content in that manner)> - <Percentages> - <Economics> - <difficulty_level: 4>	553	3	2	Optimal Price Setting in the Quirky Market Town Bakery	In a peculiar market town renowned for its extravagant economic festivals, a baker operates a quaint bakery. Last month, the baker decided to introduce a new line of prestige pastries priced at \\$4 each, hoping to increase his market share. He sold 150 pastries. Due to a pricing error, the baker also inadvertently marked down his classic cookies, which are normally priced at \\$2 each, by 25\\% to attract more customers. This resulted in the sale of 300 cookies in the same time frame. After observing that customers preferred cookies over pastries, the baker raised the prices of both items for the upcoming month. The new prices for pastries and cookies were set to be calculated based on the sales data from last month. If the market's demand fluctuated by a further 40\\% increase in cookie sales and a proportional decrease in pastry sales next month, what will be the best way to ascertain the optimal new prices to maintain profitability while ensuring that demand continues to grow? Consider how to best calculate the effects of price changes on the total revenue of both product lines before re-evaluating the price adjustments for the next month, taking into account both the price elasticity of demand and the new sales forecasts.	4	0	0	{}	2025-02-07 06:46:50.593	2025-02-07 06:46:50.593	f	\N	\N	f	{"solution": "<p>To find the optimal new prices for maintaining profitability while ensuring sales growth, we can break down the calculations as follows:</p><ol><li><p>The discounted price of cookies was calculated based on a 25% markdown:</p> <p>Cookie Price (Discounted) = \\\\$2 \\\\times (1 - 0.25) = \\\\$1.50</p></li><li><p>The total revenue generated from both pastries and cookies in the initial month was:</p> <p>Total Revenue (Initial) = (\\\\$4 \\\\times 150) + (\\\\$1.50 \\\\times 300) = \\\\$1050</p></li><li><p>With a projected 40% increase in cookie sales, the new forecast for cookie sales becomes:</p> <p>Cookie Sales (Forecasted) = 300 \\\\times (1 + 0.40) = 420</p></li><li><p>Conversely, the expected change in pastry sales, given a proportional decrease, can be anticipated as:</p> <p>Pastry Sales (Forecasted) = 150 \\\\times (1 - 0.40) = 90</p></li><li><p>Finally, estimating the total revenue for the following month with these projections keeping cookie prices at their standard current level:</p><p>Total Revenue (Forecasted) = (\\\\$4 \\\\times 90) + (\\\\$2 \\\\times 420) = \\\\$1200</p></li></ol><p>By assessment and retaining a firm grasp on both price elasticity and shifting market demands, the baker may now explore adjustments to optimize his prices after considering these revenue projections.</p>"}	\N
MCQ-Single	<Real Contextual> - <Word Problems> - <Mathematical tools(Questions which may have 2 or more mathematical approachs to solve, but user would have to choose the most optimal and efficient approach: generate question content in that manner)> - <Algebraic Equations> - <Resource Management> - <difficulty_level: 1>	554	3	2	Optimal Fishing Strategies: Balancing Demand and Sustainability on the Island	In a small island community, the local fishery has a sustainable fishing limit of 600 pounds per week. Due to an increase in demand, the fishery has decided to reassess its weekly fishing practices. The fishery currently operates $5.00 for every pound of fish caught and has fixed costs amounting to $300. The fishery's owner estimates that reducing fishing days from 6 to 4 would decrease the maximum capacity of fish caught significantly. Determine how many pounds of fish can be caught per day if they decide to fish only on 4 days this week while not exceeding the sustainable limit.	1	0	0	{}	2025-02-07 06:46:50.627	2025-02-07 06:46:50.627	f	\N	\N	f	{"solution": "To determine how many pounds of fish can be caught per day when fishing only on 4 days, we divide the total sustainable limit by the number of days fished. The calculation is as follows:<br><br>$$\\\\text{Pounds per day} = \\\\frac{\\\\text{Total Limit per Week}}{\\\\text{Fishing Days}} = \\\\frac{600 \\\\text{ pounds}}{4} = 150 \\\\text{ pounds per day}.$$<br><br>Thus, they can catch 150 pounds of fish per day."}	\N
MCQ-Single	<Pure Contextual> - <Algebra> - <Number Picking(by logical and critical reasoning over constraints given in the question)> - <Inequalities> - <difficulty_level: 2>	555	3	2	Velocity of a Comet: Determining Minimum Speed for Celestial Records	In a rare cosmic event, a particularly bright comet is traveling through our solar system. The velocity of the comet can be described by the inequality \\(v > 100 + 2x\\), where \\(v\\) is the velocity in kilometers per hour, and \\(x\\) is the number of days from its closest approach to Earth. If the comet passed by Earth 10 days ago, what is the minimum speed \\(v\\) at which the comet is traveling today, considering the influence of gravitational pull from neighboring celestial bodies that can alter its acceleration by up to 15 km/h? Express your answer in terms of \\(v\\) and determine the greatest possible rank that this comet could achieve in the top celestial speed records, keeping in mind that the velocity must exceed the average limit of 120 km/h required for such an accolade.	2	0	0	{}	2025-02-07 06:46:50.66	2025-02-07 06:46:50.66	f	\N	\N	f	{"solution": "<h2>Solution:</h2><p>Given the inequality for velocity \\\\(v > 100 + 2x\\\\), we first substitute \\\\(x = 10\\\\):</p><p>\\\\(v > 100 + 2(10) \\\\Rightarrow v > 100 + 20 \\\\Rightarrow v > 120\\\\)</p><p>Next, we need to factor in the influence from gravitational pull, which can add up to 15 km/h:</p><p>\\\\(v > 120 + 15 \\\\Rightarrow v > 135\\\\)</p><p>However, since we are looking for the greatest possible rank, we also need it to be above the average limit required for such accolade, which is 120 km/h. Thus:</p><p>\\\\(v = 135 \\\\text{ km/h} \\\\text{ (considering acceleration)}\\\\)</p><p>Therefore, the comet's speed must exceed \\\\(120 km/h\\\\) to achieve a record, confirmed by our findings:</p><p>Final minimum speed \\\\(v = 135 \\\\text{ km/h}\\\\</p>"}	\N
MCQ-Single	<Real Contextual> - <Arithmetic> - <Logical Reasoning> - <Trial and Error Method(type of questions)> - <difficulty_level: 2>	556	3	2	Calculation of Average Delivery Time in a Logistics Company	A logistics company is assessing its delivery system efficiency. They discovered that on Mondays, the average delivery time for packages is 8 hours. On Tuesdays, due to a temporary increase in workload, the average delivery time jumps to 10 hours. The company needs to calculate the average delivery time over the course of a week (Monday to Sunday). However, they realized that Wednesdays have a 20% reduction in delivery time compared to Mondays, while Thursdays have an increase of 15% compared to Tuesdays. Fridays are particularly busy, and their average delivery time is 12 hours, while Saturday deliveries are known to be quicker, averaging 7 hours. Finally, Sundays have a delivery time that is 25% longer than Saturdays. Given this information, what is the average delivery time across the entire week if the company is able to compute the total hours and divide by 7?	2	0	0	{}	2025-02-07 06:46:50.688	2025-02-07 06:46:50.688	f	\N	\N	f	{"solution": "To solve for the average delivery time over the week, we first calculate the individual delivery times:\\n<ul><li>Monday: 8 hours</li><li>Tuesday: 10 hours</li><li>Wednesday: 6.40 hours (20% reduction from Monday)</li><li>Thursday: 11.50 hours (15% increase from Tuesday)</li><li>Friday: 12 hours</li><li>Saturday: 7 hours</li><li>Sunday: 8.75 hours (25% longer than Saturday)</li></ul>Next, we find the total delivery time for the week:\\nTotal Delivery Time = 8 + 10 + 6.40 + 11.50 + 12 + 7 + 8.75\\nTotal Delivery Time = 63.65 hours\\n\\nFinally, to find the average delivery time:\\nAverage Delivery Time = \\\\frac{\\\\text{Total Delivery Time}}{7} = \\\\frac{63.65}{7} \\\\approx 9.09 \\\\text{ hours}."}	\N
MCQ-Single	<Pure Contextual> - <Word Problems> - <Setting up proper steps(questions that require users to properly setting up the steps to solve the questions)> - <Functions> - <Strategy and Management> - <difficulty_level: 1>	557	3	2	Calculating the Consulting Fee for a Startup Project	A small startup company specializes in providing strategic management consulting for various businesses. The consulting fee they charge is structured based on the functions involved in the project, specifically on the number of hours dedicated to the client's needs. For a particular project, they charge \\$100 per hour for the first 10 hours, and for any hours beyond that, they offer a 10\\% discount on the hourly rate. If a client requires 15 hours of consulting, what will be the total fee for the project?	1	0	0	{}	2025-02-07 06:46:50.716	2025-02-07 06:46:50.716	f	\N	\N	f	{"solution": "<html><p>To calculate the total consulting fee for the client, we will follow these steps:</p><ol><li>Calculate the fee for the first 10 hours:</li><p>\\\\( \\\\text{Fee for first 10 hours} = \\\\$100 \\\\times 10 = \\\\$1000 \\\\)</p><li>Determine the number of additional hours needed:</li><p>\\\\( \\\\text{Additional hours} = 15 - 10 = 5 \\\\text{ hours} \\\\)</p><li>Calculate the discounted hourly rate for additional hours:</li><p>\\\\( \\\\text{Discounted rate} = \\\\$100 \\\\times (1 - 0.10) = \\\\$90 \\\\)</p><li>Calculate the fee for the additional hours:</li><p>\\\\( \\\\text{Fee for additional hours} = \\\\$90 \\\\times 5 = \\\\$450 \\\\)</p><li>Finally, sum both fees to find the total:</li><p>\\\\( \\\\text{Total fee} = \\\\$1000 + \\\\$450 = \\\\$1450 \\\\)</p></ol></html>"}	\N
MCQ-Single	<Pure Contextual> - <Algebra> - <Backsolving> - <Inequalities> - <difficulty_level: 1>	558	3	2	Weight Combinations of Fruits in a Market Basket	In a quaint village, there are three types of fruits being sold at a local market. Apples are sold at \\$2 per kilogram, oranges at \\$3 per kilogram, and bananas at \\$1 per kilogram. A fruit vendor determines to mix these fruits and put together a fruit basket weighing a total of 10 kilograms. If the vendor wants to ensure that the weight of bananas is at least 2 kilograms but not more than 4 kilograms, how many kilograms of apples and oranges combined does the vendor need to include in the basket, provided that the weight of apples must be twice that of oranges? What are the possible weight combinations for apples and oranges under these constraints?	1	0	0	{}	2025-02-07 06:46:50.746	2025-02-07 06:46:50.746	f	\N	\N	f	{"solution": "<p>To solve the problem, we start by expressing the weight of apples and oranges using the given relationships:</p> <p>Let:</p> <ul> <li>Weight of apples = a</li> <li>Weight of oranges = o</li> <li>Weight of bananas = b</li> </ul> <p>According to the problem:</p> <ul> <li>The relationship between apples and oranges is: \\\\( a = 2o \\\\)</li> <li>And the total weight equation is: \\\\( a + o + b = 10 \\\\)</li> </ul> <p>Substituting the expression for apples into the total weight equation gives:</p> <p>\\\\( 2o + o + b = 10 \\\\)</p> <p>This simplifies to:</p> <p>\\\\( 3o + b = 10 \\\\)</p> <p>From this, we can express the weight of bananas as:</p> <p>\\\\( b = 10 - 3o \\\\)</p> <p>Next, we have the constraints for the weight of bananas:</p> <ul> <li>Minimum weight of bananas: \\\\( b \\\\geq 2 \\\\)</li> <li>Maximum weight of bananas: \\\\( b \\\\leq 4 \\\\)</li> </ul> <p>Setting these inequalities we find:</p> <p>For minimum weight:</p> <p>\\\\( 10 - 3o \\\\geq 2 \\\\Rightarrow 3o \\\\leq 8 \\\\Rightarrow o \\\\leq \\\\frac{8}{3} \\\\approx 2.67 \\\\)</p> <p>For maximum weight:</p> <p>\\\\( 10 - 3o \\\\leq 4 \\\\Rightarrow 3o \\\\geq 6 \\\\Rightarrow o \\\\geq 2 \\\\)</p> <p>Thus, the possible values of weight of oranges satisfying the conditions are approximately:</p> <ul> <li>2 kg</li> <li>2.33 kg</li> <li>2.67 kg</li> </ul> <p>Therefore, the combined weight of apples and oranges must be represented within these conditions.</p>"}	\N
MCQ-Single	<Real Contextual> - <Arithmetic> - <Critical Reasoning> - <Ratio and Proportion> - <difficulty_level: 1>	559	3	2	Finding the Number of Chocolate Muffins in a Bakery Based on Ratios	In a local bakery, the ratio of chocolate muffins to blueberry muffins is 4:3. If there are a total of 70 muffins in the bakery, how many chocolate muffins are there? To solve the problem, you must find the total parts represented by the ratio and then determine the portion that corresponds to chocolate muffins.	1	0	0	{}	2025-02-07 06:46:50.773	2025-02-07 06:46:50.773	f	\N	\N	f	{"solution": "To find the number of chocolate muffins, follow these steps:<br>1. The ratio of chocolate muffins to blueberry muffins is given as 4:3.<br>2. First, calculate the total parts in the ratio: \\\\(4 + 3 = 7\\\\).<br>3. To find the number of chocolate muffins, use the ratio: \\\\(\\\\frac{4}{7} \\\\times 70 = 40\\\\).<br>Thus, the total number of chocolate muffins is \\\\(40\\\\)."}	\N
MCQ-Single	<Pure Contextual> - <Arithmetic> - <Logical Reasoning> - <Unitary Method> - <difficulty_level: 2>	560	3	2	Earnings Comparison of Two Farmers at the Strawberry Festival	In a peculiar town known for its annual strawberry festival, the local farmers decided to distribute their strawberries in unique ways to attract more visitors. Farmer A sells his strawberries at a price of \\$3 per kilogram, while Farmer B sells his strawberries at \\$4 per kilogram. This year, Farmer A managed to sell 36 kilograms, which resulted in total proceeds of \\$108. Meanwhile, Farmer B reported an interesting outcome this season; for every kilogram sold, he noticed that if he sold twice as many kilograms as Farmer A, his earnings would total \\$X. If Farmer B sold 25 kilograms of strawberries this season, how much did he earn in total, and was he correct in his assumption? Calculate the total earnings and provide an explanation for the values used in your calculations.	2	0	0	{}	2025-02-07 06:46:50.802	2025-02-07 06:46:50.802	f	\N	\N	f	{"solution": "<p>Farmer A sold his strawberries at a price of \\\\$3 per kilogram. He sold 36 kilograms. The total earnings for Farmer A can be calculated as:</p>\\n\\n<p>\\\\(\\\\text{Total Earnings of Farmer A} = \\\\text{Price} \\\\times \\\\text{Kilograms Sold} = 3 \\\\times 36 = \\\\$108\\\\)</p>\\n\\n<p>Farmer B sells his strawberries at \\\\$4 per kilogram. He sold 25 kilograms. The total earnings for Farmer B can be calculated as:</p>\\n\\n<p>\\\\(\\\\text{Total Earnings of Farmer B} = \\\\text{Price} \\\\times \\\\text{Kilograms Sold} = 4 \\\\times 25 = \\\\$100\\\\)</p>\\n\\n<p>Thus, Farmer A earned \\\\$108 while Farmer B earned \\\\$100.</p>"}	\N
MCQ-Single	<Pure Contextual> - <Algebra> - <Backsolving> - <Algebraic Equations> - <difficulty_level: 5>	561	3	2	Finding the Number of Students and Schools in a Town Based on Given Equations	In a certain town, the population is represented by the equation 2x + 3y = 79 and the number of schools is given by y = \\frac{b}{x} + 5, where x represents the number of students and y represents the number of schools. If it is known that the number of students exceeds 40 by at least 7, which of the following values of x would satisfy both equations under the restriction that y must be an integer?	5	0	0	{}	2025-02-07 06:46:50.83	2025-02-07 06:46:50.83	f	\N	\N	f	{"solution": "To solve for the number of students (x) and schools (y), we start with the two equations given:<br> <br> 1. \\\\( 2x + 3y = 79 \\\\) <br> 2. \\\\( y = \\\\frac{8}{x} + 5 \\\\)<br> <br> Substituting the second equation into the first gives us:<br> \\\\( 2x + 3\\\\left(\\\\frac{8}{x} + 5\\\\right) = 79 \\\\)<br> Simplifying this equation leads to:<br> \\\\( 2x + \\\\frac{24}{x} + 15 = 79 \\\\)<br> which further reduces to:<br> \\\\( 2x + \\\\frac{24}{x} = 64 \\\\)<br> Multiplying through by x to eliminate the fraction results in:<br> \\\\( 2x^{2} - 64x + 24 = 0 \\\\)<br> Solving this quadratic equation using the quadratic formula yields two potential values for x:<br> \\\\( x = 16 - 2\\\\sqrt{61} \\\\) and \\\\( x = 2\\\\sqrt{61} + 16 \\\\).<br> Since we are looking for the integer value where the number of students exceeds 47 by 7, we take the second potential value which results in approximately 31.62. Therefore, the valid choice for the number of students is around 31, ensuring y remains an integer."}	\N
		786	1	1	Expected Sales Revenue from Advertising Budget Increase to $50,000	Based on the scatter plot illustrating the relationship between advertising budget and sales, if the advertising budget was increased to 50 thousand dollars, what would be the expected sales revenue based on the trend observed in the data?	1	0	0	{}	2025-02-08 05:11:42.651	2025-02-08 05:11:42.651	t	83	42	t	{"solution": "The expected sales revenue for an advertising budget of $50,000 is approximately $55.07."}	12
MCQ-Single	<Real Contextual> - <Algebra> - <Backsolving> - <Inequalities> - <difficulty_level: 3>	562	3	2	Inequalities in Theatre Ticket Sales	In a local theatre, the management has decided to set up an event where tickets are sold in two categories: Category A, which costs \\$15 each, and Category B, which costs \\$25 each. The theatre has a maximum seating capacity of 200 and seeks to achieve at least \\$3,000 in total ticket sales. If the number of tickets sold for Category A is represented by x and the number of tickets sold for Category B is represented by y, which of the following inequalities correctly represents the situation described, taking into account the limits on the seating and the sales threshold?	3	0	0	{}	2025-02-07 06:46:50.862	2025-02-07 06:46:50.862	f	\N	\N	f	{"solution": "<p>To represent the data given in the problem, we start with two key inequalities:</p>\\n<ul>\\n<li>1. The total ticket revenue must be at least \\\\$3000:</li>\\n<p>\\\\(15x + 25y \\\\geq 3000\\\\)</p>\\n<li>2. The total number of tickets sold must not exceed the seating capacity of 200:</li>\\n<p>\\\\(x + y \\\\leq 200\\\\)</p>\\n</ul>\\n<p>Now, we can solve each inequality for y:</p>\\n<ul>\\n<li>From the first inequality:</li>\\n<p>\\\\(y \\\\geq 120 - \\\\frac{3}{5}x\\\\)</p>\\n<li>From the second inequality:</li>\\n<p>\\\\(y \\\\leq 200 - x\\\\)</p>\\n</ul>\\n<p>With these derived expressions of y, we can analyze the constraints on ticket sales and seating arrangements.</p>"}	\N
MCQ-Single	<Real Contextual> - <Arithmetic> - <Number Sense> - <Percentages> - <difficulty_level: 5>	563	3	2	Florist's Pricing Dilemma: Calculating Minimum Selling Price for Wedding Arrangements	In a region known for its rare and exquisite flowers, a boutique florist specializes in creating stunning floral arrangements for various occasions. One day, the florist received an order for a grand wedding event that requested 150 white roses, 200 red tulips, and 250 blue orchids. Each type of flower has a different price based on its rarity. The white roses are priced at $3 each, the red tulips at $2.5 each, and the blue orchids at $4 each. As the florist plans the arrangement, they also need to consider an extra budget of 15% for transportation costs and a 10% discount on the total price due to a special vendor relationship. If the florist wants to achieve a profit margin of at least 20% on the final price, what should be the minimum selling price that the florist should charge for the wedding arrangements? Take each step carefully to ensure all costs, discounts, and desired profits are accurately considered, and calculate the final amount the florist should charge, rounding to the nearest cent.	5	0	0	{}	2025-02-07 06:46:50.889	2025-02-07 06:46:50.889	f	\N	\N	f	{"solution": "Solution not available"}	\N
CR	<philosophy> - <CR> - <draw inference/conclusion> - <difficulty_level: 4>	564	4	2	Inferences on Utilitarianism's Impact on Ethical Decisions	Based on the philosophy of utilitarianism discussed in the passage, what can be inferred about its influence on modern ethical decision-making?	4	0	0	{"passages": ["In recent years, a new philosophy has emerged advocating for the significance of emotional intelligence over traditional cognitive intelligence. Proponents argue that understanding and managing emotions is fundamental not only in personal relationships but also in professional environments. They assert that leaders who possess high emotional intelligence are more effective in fostering teamwork and motivating their subordinates. Furthermore, studies indicate that teams led by emotionally intelligent leaders tend to outperform those led by leaders lacking in this skill. Critics, however, question whether emotional intelligence is truly more important than cognitive intelligence in decision-making processes. They cite instances where analytical skills and technical knowledge have led to significant breakthroughs in various fields. As the debate continues, many organizations are starting to prioritize emotional intelligence training alongside traditional cognitive skill development.", "The philosophy of utilitarianism posits that the best action is the one that maximizes utility, generally defined as that which produces the greatest well-being of the greatest number of people. This approach is often applied in ethical reasoning and policy-making. Proponents of utilitarianism argue that it provides a clear framework for evaluating the consequences of actions and choices. However, critics claim that utilitarianism can sometimes lead to morally questionable decisions if the overall utility justifies harming a minority. Despite these criticisms, recent studies in social behavior indicate that societies tend to favor utilitarian principles when making collective decisions, suggesting that such philosophies may strongly influence public policy and societal norms. As more leaders and policymakers embrace these principles, there is a growing question about the long-term implications of utilitarianism on ethical standards and individual rights."]}	2025-02-07 06:46:50.919	2025-02-07 06:46:50.919	f	\N	\N	f	{"solution": "The correct answer is B: <br> Utilitarian principles likely contribute to a more collective approach in ethical decision-making. The passage indicates that societies tend to favor utilitarian principles when making collective decisions, suggesting a significant influence on modern ethical reasoning. <o> <br> Option A is incorrect because the passage does not state that utilitarianism has been completely rejected; rather, it highlights an ongoing debate. <o> <br> Option C is incorrect, as the passage emphasizes that utilitarianism may lead to morally questionable decisions, but it does not imply that individual rights are prioritized. <o> <br> Option D is incorrect because the passage suggests that utilitarianism does influence public policy, indicating its relevance and effectiveness. <o> <br> Option E is also incorrect as it contradicts the evidence presented in the passage regarding the acceptance of utilitarian principles in social decision-making."}	\N
CR	<physical_sciences> - <CR> - <complete the argument> - <difficulty_level: 1>	565	4	2	Completing the Argument on Physical Activity Benefits in Schools	Which of the following, if true, would most logically complete the argument presented in the passage about the benefits of physical activity in schools?	1	0	0	{"passages": ["Recent advancements in solar energy technology have made it significantly more efficient and accessible. As a result, many households are not only adopting solar panels for their energy needs but are also selling excess energy back to the grid. This shift indicates a move toward a more sustainable and economically viable energy future. Therefore, if more households transition to solar energy technologies, the overall carbon footprint of residential energy consumption will be greatly reduced.", "In recent years, researchers have discovered that exercise has not only physical benefits but also significant mental health benefits. Studies show that regular physical activity can alleviate symptoms of anxiety and depression. This is particularly important as mental health issues continue to rise globally. Therefore, if schools incorporate more physical activity into their curriculums, students will likely experience improved mental health and overall well-being."]}	2025-02-07 06:46:50.937	2025-02-07 06:46:50.937	f	\N	\N	f	{"solution": "The correct answer is E. Research shows that students who engage in physical activity have lower stress levels, which directly supports the argument that incorporating physical activity into school curriculums will improve mental health and overall well-being.<br><o>Option A is incorrect because while it mentions barriers to participation, it does not strengthen the conclusion about the positive impacts of exercise on mental health.<br><o>Option B is incorrect because, although it discusses academic performance, it does not explicitly address mental health benefits.<br><o>Option C is incorrect as it introduces a negative aspect of physical activity but fails to complete the argument in a way that supports the conclusion.<br><o>Option D is also incorrect since it highlights student preferences for sedentary activities, which undermines the argument rather than completing it."}	\N
CR	<culture> - <CR> - <draw inference/conclusion> - <difficulty_level: 1>	566	4	2	Impact of Social Media on Youth Culture	Based on the passage, what can be concluded about the impact of social media on youth culture?	1	0	0	{"passages": ["In recent years, a significant rise in vegetarianism has been observed in urban populations across various countries. This increase is often attributed to heightened awareness of health issues, environmental concerns, and animal rights. In many cities, vegetarian restaurants are flourishing, and more grocery stores are stocking plant-based products than ever before. Surveys indicate that younger generations are particularly inclined towards adopting vegetarian diets, suggesting that this trend may lead to lasting changes in dietary habits. Given these observations, it can be inferred that urban culture is evolving to become more health-conscious and ethical.", "Recent studies have shown that social media platforms are profoundly influencing youth culture. Teenagers increasingly rely on these platforms for entertainment, information, and connection with peers. As a result, traditional forms of communication, such as face-to-face interactions and phone calls, have seen a decline. Furthermore, a survey revealed that 75% of teenagers prefer to share experiences online rather than in person. This evidence suggests that social media not only shapes their interests and opinions but also alters the way they build relationships, indicating a shift in cultural norms among younger generations."]}	2025-02-07 06:46:50.954	2025-02-07 06:46:50.954	f	\N	\N	f	{"solution": "The correct answer is B: Teenagers are increasingly sharing experiences online over traditional communication methods.<br> This statement accurately reflects the passage's conclusion that teenagers prefer to share their experiences on social media rather than through face-to-face interactions, indicating a shift in cultural norms.<br> <o>Option A is incorrect because the passage states that traditional forms of communication, such as face-to-face interactions, have declined due to social media use.<br> <o>Option C is incorrect as the passage does not mention any increased popularity of traditional media sources.<br> <o>Option D is incorrect because the passage clearly indicates that social media has a significant influence on how teenagers connect with one another.<br> <o>Option E is incorrect as the passage does not discuss teenagers' preferences for obtaining information from books over online sources."}	\N
CR	<social_sciences> - <CR> - <draw inference/conclusion> - <difficulty_level: 4>	567	4	2	Impacts of Public Libraries on Civic Engagement	Based on the findings of the study by the Institute for Urban Development, which of the following conclusions can be drawn regarding public libraries and civic engagement?	4	0	0	{"passages": ["Recent research shows that urban parks significantly enhance the quality of life for city residents. A study conducted in various metropolitan areas revealed that individuals living near parks reported higher levels of physical activity, improved mental health, and greater community engagement. Despite these positive outcomes, many urban parks are underfunded and suffer from neglect. Consequently, urban planners argue that investment in parks is crucial for fostering healthy communities. The data suggests that increased park funding could lead to better public health outcomes. However, some critics claim that the benefits of parks are overstated and that funds could be allocated to other pressing needs, such as housing or transportation infrastructure.", "A recent study by the Institute for Urban Development found that people who utilize public libraries are more likely to be involved in civic activities, such as volunteering and voting, than those who do not. The study surveyed several communities and noted that in areas with well-resourced libraries, residents engaged in democratic processes at significantly higher rates. Library advocates argue that this indicates a link between access to information and active civic participation. However, skeptics remind us that correlation does not imply causation, suggesting that those who frequent libraries might already be inclined towards civic involvement for other reasons. This leads to an ongoing debate about the true impact of public libraries on community engagement."]}	2025-02-07 06:46:50.97	2025-02-07 06:46:50.97	f	\N	\N	f	{"solution": "The correct answer is D: The findings support the idea that using libraries correlates with increased civic participation.<br> <o>This option is directly supported by the study's conclusion that users of public libraries engage more in civic activities compared to non-users.</o><br> <o>Option A is too strong, as it states libraries are essential, while the study only shows correlation, not causation.</o><br> <o>Option B introduces an unrelated variable—education—without evidence from the passage.</o><br> <o>Option C incorrectly states that access to libraries has no relationship with voting rates, contradicting the findings of increased civic activity.</o><br> <o>Option E is misleading as it suggests that only well-resourced libraries have an impact, while the passage does not isolate the effect of resource levels.</o>"}	\N
		787	1	1	Expected Sales Revenue from Social Media Marketing Budget Reduction to $10,000	According to the scatter plot depicting the impact of social media marketing on sales, if the social media marketing budget were to be reduced to 10 thousand dollars, what sales revenue would you expect based on the observed trend in the data?	1	0	0	{}	2025-02-08 05:11:42.67	2025-02-08 05:11:42.67	t	83	42	t	{"solution": "The expected sales revenue for a social media marketing budget of $10,000 is approximately $26.84."}	12
CR	<philosophy> - <CR> - <evaluate the conclusion> - <difficulty_level: 1>	568	4	2	Evaluating Conclusions on Moral Relativism in Ethical Debates	Based on the passage, which of the following conclusions can be accurately drawn regarding moral relativism and its implications for ethical debates?	1	0	0	{"passages": ["Philosophers often argue about the nature of truth and its relationship to reality. Some contend that truth is an objective characteristic, independent of human perception, while others believe that truth is subjective, shaped by cultural and individual contexts. A recent debate highlighted this divide, with proponents of objective truth arguing that scientific discoveries reveal universal truths about the world, while advocates for subjective truth claim that different perspectives can lead to equally valid interpretations of realities. Ultimately, the discussion poses critical questions about how we evaluate the conclusions we draw from our experiences and observations.", "In philosophy, the concept of moral relativism suggests that moral judgments are not absolute but rather shaped by cultural, societal, and personal influences. Proponents argue that what is considered right or wrong can vary from one society to another, and as such, no single moral framework should be viewed as superior. This position raises important considerations for ethical debates, as it challenges the validity of universal moral principles. Critics, however, argue that this view can lead to a dangerous tolerance of harmful practices, suggesting a need for some overarching moral standards. Thus, the ongoing discourse about moral relativism and its implications invites us to critically evaluate the conclusions drawn about ethics in a diverse world."]}	2025-02-07 06:46:50.987	2025-02-07 06:46:50.987	f	\N	\N	f	{"solution": "The correct answer is C: Critics of moral relativism argue for the necessity of universal moral standards to prevent harm.<br><o>This option accurately reflects the passage's discussion about how critics of moral relativism see the potential dangers of a lack of absolute ethical guidelines.</o><br><o>Option A is incorrect because it misrepresents moral relativism; while it recognizes different moral perspectives, it does not claim they are all equally valid without context.</o><br><o>Option B is also incorrect as it suggests that proponents of moral relativism advocate for a singular dominant perspective, which contradicts their fundamental belief in the multiplicity of moral views.</o><br><o>Option D is misleading since moral relativism recognizes that ethical practices may differ across cultures, implying that practices can evolve over time.</o><br><o>Lastly, option E is incorrect because the debate on moral relativism is highly relevant to contemporary ethical discussions, as evidenced by ongoing ethical dilemmas in diverse societies.</o>"}	\N
CR	<philosophy> - <CR> - <find the assumption> - <difficulty_level: 2>	569	4	2	Identify the assumption in deontological ethics regarding moral actions	What assumption is made by the proponent of deontological ethics in the argument presented regarding moral actions and their consequences?	2	0	0	{"passages": ["The philosophical notion of utilitarianism posits that the best action is one that maximizes utility, typically defined as that which produces the greatest well-being of the greatest number of people. Some critics argue that this approach fails to take into account the long-term consequences of actions, focusing instead on immediate outcomes. However, proponents claim that by prioritizing overall happiness, utilitarianism leads to more ethical decision-making. Therefore, they argue that when faced with a moral dilemma, one should always opt for the course of action that benefits the majority.", "In examining moral philosophies, one often encounters deontological ethics, which assert that the morality of an action is based on whether that action itself is fundamentally right or wrong, regardless of the consequences. This view is contrasted with consequentialist theories, which judge actions based on their outcomes. A common assumption underlying deontological perspectives is that there are inherent moral rights and duties that do not depend on the potential results of an action. Thus, when making ethical decisions, it is crucial to recognize these moral imperatives."]}	2025-02-07 06:46:51.003	2025-02-07 06:46:51.003	f	\N	\N	f	{"solution": "<o>The correct answer is B: 'There are actions that are inherently right or wrong regardless of outcomes.' This statement captures the core assumption of deontological ethics, which posits that moral actions are judged based on their own intrinsic nature rather than their consequences.</o><br><o>Option A is incorrect because it contradicts the foundational principle of deontology, which emphasizes that moral rights and duties exist independently of consequences.</o><br><o>Option C is incorrect as it references a consequentialist perspective rather than a deontological one, which does not prioritize outcomes in moral decision-making.</o><br><o>Option D is incorrect because it advocates for consequentialism, which deontological ethics explicitly stands against.</o><br><o>Option E is incorrect as it conflates deontological ethics with a perspective that prioritizes individual happiness over collective good, which is not a tenet of deontology.</o>"}	\N
CR	<culture> - <CR> - <paradox> - <difficulty_level: 1>	570	4	2	Understanding the Paradox of Cultural Identity and Transformation	What is the paradox presented in the passage concerning cultural identity and its transformation?	1	0	0	{"passages": ["In many societies, cultural practices are often seen as rigid and unchanging. However, historical evidence suggests that cultures are not static; they evolve over time in response to various factors such as globalization, technological advancements, and social movements. This presents a paradox: while many individuals may strongly identify with and cling to their cultural traditions, these very traditions may be changing or disappearing as society progresses. Hence, the question arises: how can a culture be both a source of identity and a subject to transformation?", "Cultural identity is often perceived as a fixed and uniform characteristic that individuals possess. Yet, the reality is often contradictory. On one hand, people take pride in their heritage and maintain traditions that have been passed down through generations. On the other hand, exposure to different cultures through travel, migration, or technology frequently leads individuals to adopt new practices and beliefs that may dilute their original cultural identities. This raises a paradox: how can one claim to uphold their cultural heritage while simultaneously embracing influences from other cultures?"]}	2025-02-07 06:46:51.02	2025-02-07 06:46:51.02	f	\N	\N	f	{"solution": "The correct answer is B: <br> Cultural practices evolve in response to external influences while still being embraced by individuals. This option reflects the paradox described in the passage, where individuals maintain a sense of cultural identity even as they adapt to new influences. <br> <o> Option A is incorrect because it ignores the dynamic nature of cultural identity that the passage discusses. <br> <o> Option C is incorrect as it suggests that outside influences must be completely rejected, contradicting the concept of cultural evolution presented in the passage. <br> <o> Option D is incorrect because the passage implies that cultural transformation has been ongoing throughout history, not just a recent phenomenon. <br> <o> Option E is also incorrect because it fails to recognize that cultural identity can, and often does, incorporate change and adapt over time."}	\N
CR	<history> - <CR> - <complete the argument> - <difficulty_level: 1>	571	4	2	Completion of the Argument on the Renaissance's Impact	Based on the passage, which of the following best completes the argument: 'Thus, the Renaissance not only revived classical knowledge but also ________.'	1	0	0	{"passages": ["The ancient Greeks made significant contributions to the fields of art, science, and philosophy, which have continued to influence modern civilization. For instance, their development of democratic principles laid the foundation for contemporary political systems. Furthermore, their innovative approaches in mathematics and geometry, such as the Pythagorean theorem, have shaped the way we understand the world today. Therefore, one can argue that without the contributions of the ancient Greeks, our understanding of democracy, art, and science would be markedly different.", "During the Renaissance period, a revival of interest in classical knowledge began to spread across Europe. This movement not only led to advancements in art and architecture but also spurred significant progress in science and technology. For example, Leonardo da Vinci's studies of anatomy improved our understanding of the human body, while Galileo's innovations in astronomy changed how we perceive our place in the universe. Therefore, it can be concluded that the Renaissance was a pivotal time that not only celebrated the achievements of ancient civilizations but also laid the groundwork for modern scientific inquiry."]}	2025-02-07 06:46:51.036	2025-02-07 06:46:51.036	f	\N	\N	f	{"solution": "The correct answer is A: 'initiated a new era of artistic expression and scientific exploration.' This option logically follows the passage's argument that the Renaissance built upon classical knowledge and contributed significantly to advancements in various fields.<br> <o>Option B is incorrect because the passage highlights significant progress in philosophical thought during the Renaissance.</o> <br> <o>Option C is incorrect as the passage clearly states the profound impact of the Renaissance on modern society.</o> <br> <o>Option D is inaccurate because the passage discusses broader achievements beyond just the revival of Greek art.</o> <br> <o>Option E is also incorrect since the passage emphasizes advancements in technology and science rather than restrictions.</o>"}	\N
CR	<history> - <CR> - <strengthen the argument> - <difficulty_level: 1>	572	4	2	Strengthening the Argument for the Printing Press's Role in the Renaissance	Which of the following, if true, would most strengthen the argument that the printing press was instrumental in shaping the transformative nature of the Renaissance?	1	0	0	{"passages": ["Throughout history, many civilizations have thrived primarily due to their innovations in agricultural practices. For instance, the ancient Mesopotamians developed irrigation systems that allowed them to control water flow, which in turn significantly boosted their crop yields. This advancement in agriculture helped sustain larger populations and facilitated trade. Consequently, it is clear that agricultural innovation is not merely a supportive element but a critical factor in the success and expansion of civilizations.", "The Renaissance, a period of significant cultural and intellectual revival in Europe, was largely fueled by the increased availability of printed materials. The invention of the printing press allowed for the rapid dissemination of ideas, particularly those related to science and philosophy. This surge in accessible knowledge not only inspired advancements in various fields but also empowered individuals to challenge traditional beliefs. Therefore, it can be posited that the printing press was instrumental in shaping the transformative nature of the Renaissance."]}	2025-02-07 06:46:51.053	2025-02-07 06:46:51.053	f	\N	\N	f	{"solution": "The correct answer is C. This statement directly supports the argument by indicating that classical texts, which were vital to the intellectual advancements of the Renaissance, became widely accessible because of the printing press. <br> <o> Option A, while true, only discusses the limitations of handwritten manuscripts without connecting it to the transformative nature of the Renaissance. <br> <o> Option B discusses a decline in religious influence but does not directly relate to how the printing press contributed to broader knowledge dissemination. <br> <o> Option D highlights economic prosperity but does not specifically address the role of the printing press. <br> <o> Option E contradicts the argument that the printing press was instrumental in shaping the Renaissance by suggesting it was only used for religious texts, thereby weakening the overall argument."}	\N
		573	4	2	Implications of Physical Sciences in Technological Advancements	What can be inferred about the practical significance of thermodynamics, quantum mechanics, and electromagnetism in modern technology based on the passages?	-1	0	0	{}	2025-02-07 06:46:51.078	2025-02-07 06:46:51.078	t	57	\N	f	{"solution": "<p>The correct answer is <strong>A</strong>: These scientific principles are essential for the development of innovative technologies, such as renewable energy and quantum computing.</p><p>This option accurately reflects the implications drawn from the passages, which discuss how thermodynamics, quantum mechanics, and electromagnetism are not only foundational theories but also crucial for advancing technology.</p><p><strong>B</strong>: The principles of physical sciences have no significant impact on contemporary technological applications. <em>This statement is incorrect as the passages highlight the direct applications of these scientific principles in various technologies.</em></p><p><strong>C</strong>: Understanding these concepts is primarily important for academic purposes and does not influence real-world technology. <em>The passages clearly indicate that these principles are vital for practical applications, thus this option is also incorrect.</em></p><p><strong>D</strong>: Scientific advances in physics are solely confined to theoretical frameworks and do not translate into practical applications. <em>This statement contradicts the essence of the passages, which emphasize the significant real-world applications of physical sciences.</em></p>"}	\N
		574	4	2	The Transformative Role of Quantum Mechanics in Understanding Reality	What can be inferred about the role of quantum mechanics in reshaping our understanding of reality based on the passages?	-1	0	0	{}	2025-02-07 06:46:51.097	2025-02-07 06:46:51.097	t	57	\N	f	{"solution": "<p>The correct answer is <strong>A</strong>: Quantum mechanics fundamentally alters our perception of reality by introducing concepts such as wave-particle duality and entanglement.</p><p>This option accurately reflects the implications of the passage, which discusses how quantum mechanics challenges classical intuitions and prompts a reconsideration of the nature of reality.</p><p><strong>B</strong>: The principles of quantum mechanics are confirmed by classical physics, providing no significant change in our understanding of reality. <em>This statement is incorrect as the passage highlights that quantum mechanics challenges and redefines, rather than confirms, classical physics.</em></p><p><strong>C</strong>: Quantum mechanics leads to practical benefits only, without affecting theoretical frameworks. <em>This is incorrect since the passage emphasizes that quantum mechanics not only has practical applications but also alters theoretical understandings of reality.</em></p><p><strong>D</strong>: The theories in quantum mechanics support the idea that reality operates solely on deterministic principles. <em>This statement is inaccurate; the passage illustrates that quantum mechanics introduces indeterminacy and complexities that contradict purely deterministic views.</em></p>"}	\N
		575	4	2	Consequences of Maxwell's Equations in Electromagnetism	According to the passage, what is a consequence of Maxwell's equations in relation to electricity and magnetism?	-1	0	0	{}	2025-02-07 06:46:51.116	2025-02-07 06:46:51.116	t	57	\N	f	{"solution": "<p>The correct answer is <strong>A</strong>: Maxwell's equations describe how electric charges create electric fields.</p><p>This statement is directly supported by the passage, which outlines that one of the key roles of Maxwell's equations is to explain the interaction between electric and magnetic fields.</p><p><strong>B</strong>: Maxwell's equations provide an argument that electricity and magnetism are completely independent phenomena. <em>This statement is incorrect as the passage illustrates that electricity and magnetism are interconnected through Maxwell's equations.</em></p><p><strong>C</strong>: Maxwell's equations emphasize that electric currents cannot generate magnetic fields. <em>This is inaccurate; the passage states that changing magnetic fields generate electric currents, contradicting this option.</em></p><p><strong>D</strong>: Maxwell's equations state that electric fields do not influence magnetic fields. <em>This statement is also incorrect since Maxwell's equations highlight the intricate relationship between electric and magnetic fields.</em></p>"}	\N
		576	4	2	Analyzing the Interconnectedness in Physical Sciences	What is the primary strength of the argument presented in the passage regarding the interconnectedness of various scientific principles in understanding physical phenomena?	-1	0	0	{}	2025-02-07 06:46:51.14	2025-02-07 06:46:51.14	t	58	\N	f	{"solution": "<p>The correct option is <strong>A</strong>: <em>The argument highlights how advancements in one scientific field can lead to breakthroughs in others, demonstrating their mutual reliance.</em> This reflects the passage's emphasis on the interdependencies among various scientific disciplines and how they collaborate to enhance our understanding of physical phenomena.</p> <p>Option <strong>B</strong> is incorrect because it contradicts the passage's assertion that different scientific fields are interconnected rather than independent.</p> <p>Option <strong>C</strong> is incorrect as the passage does not promote a singular approach to solving climate change, but rather highlights the need for an interdisciplinary method.</p> <p>Option <strong>D</strong> is also incorrect because the passage discusses the complexities and probabilistic nature of scientific laws, not a purely deterministic perspective.</p>"}	\N
		577	4	2	Inference on Interdisciplinary Research in Global Challenges	What can be inferred from the passage about the role of interdisciplinary research in addressing global challenges?	-1	0	0	{}	2025-02-07 06:46:51.158	2025-02-07 06:46:51.158	t	58	\N	f	{"solution": "<p>The correct option is <strong>B</strong>: <em>Collaborative efforts among various scientific fields enhance the effectiveness of solutions to complex problems like climate change.</em> This inference aligns with the passage's discussion on the necessity of interdisciplinary research to understand and address environmental issues.</p> <p>Option <strong>A</strong> is incorrect because it misrepresents the passage; it suggests that interdisciplinary research is less important, while the passage advocates for its importance.</p> <p>Option <strong>C</strong> is incorrect since the passage argues for the complexity of environmental issues, implying that single-discipline studies may not suffice.</p> <p>Option <strong>D</strong> is also incorrect as the passage focuses on the significance of collaboration in scientific research, rather than suggesting motivations related to funding opportunities.</p>"}	\N
		578	4	2	Detail on the Principle of Matter and Mass	According to the passage, what scientific principle is described as providing insight into why matter has mass?	-1	0	0	{}	2025-02-07 06:46:51.176	2025-02-07 06:46:51.176	t	58	\N	f	{"solution": "<p>The correct option is <strong>C</strong>: <em>Einstein's theory of relativity</em>. The passage explicitly states that this theory provides insight into why matter has mass, particularly through the context of the Higgs boson and the Higgs field.</p> <p>Option <strong>A</strong> is incorrect because, while the standard model of particle physics is mentioned, it does not specifically address why matter has mass.</p> <p>Option <strong>B</strong> is incorrect as the laws of thermodynamics are discussed in relation to energy transformations but not directly linked to the concept of mass.</p> <p>Option <strong>D</strong> is also incorrect as the principle of superposition pertains to quantum mechanics, which does not directly explain the mass of matter as described in the passage.</p>"}	\N
		579	4	2	Primary Purpose of the Passage on Physical Sciences	What is the primary purpose of the passage regarding the field of physical sciences?	-1	0	0	{}	2025-02-07 06:46:51.194	2025-02-07 06:46:51.194	t	58	\N	f	{"solution": "<p>The correct option is <strong>B</strong>: <em>To highlight the interconnectedness of various scientific principles and the importance of interdisciplinary research.</em> The passage emphasizes how different scientific fields are connected and discusses the necessity of collaboration to address complex issues like climate change.</p> <p>Option <strong>A</strong> is incorrect because the passage does not focus on historical developments but rather on current scientific understandings and their applications.</p> <p>Option <strong>C</strong> is incorrect as the passage does not delve into specific physical laws or their mathematical formulations, but rather discusses broad principles and concepts.</p> <p>Option <strong>D</strong> is also incorrect since the passage does not present physical sciences as subjective; it discusses the objective nature of scientific inquiry and collaboration.</p>"}	\N
		580	4	2	Organizational Structure of Historical Developments	What is the primary organizational structure used in the passage to discuss the major historical events such as the Renaissance, the Age of Exploration, and the Industrial Revolution?	-1	0	0	{}	2025-02-07 06:46:51.218	2025-02-07 06:46:51.218	t	59	\N	f	{"solution": "<p>The primary organizational structure used in the passage is:</p> <p><strong>A: Chronological order emphasizing the sequence of events.</strong> This option is correct because the passage discusses historical eras in the order they occurred (Renaissance, Age of Exploration, and Industrial Revolution), clearly illustrating their chronological development.</p> <p><strong>B: Comparative analysis linking different cultural effects.</strong> This option is incorrect as the passage does not primarily compare different cultural effects in a side-by-side format, but rather presents events in a sequential manner.</p> <p><strong>C: Thematic organization focusing on technological advancements.</strong> This option is not entirely accurate, since while technology is mentioned, the passage primarily focuses on distinct historical periods rather than categorizing them thematically based only on technological advancements.</p> <p><strong>D: Discrete sections highlighting individual historical figures.</strong> This option is incorrect because the passage discusses broader historical movements rather than isolating individual figures in separate sections.</p>"}	\N
		581	4	2	Inference on the Renaissance's Influence on Science	Based on the passage, what inference can be drawn about the impact of the Renaissance on future scientific developments?	-1	0	0	{}	2025-02-07 06:46:51.242	2025-02-07 06:46:51.242	t	59	\N	f	{"solution": "<p>The correct answer is:</p> <p><strong>C: The emphasis on humanism during the Renaissance encouraged scientific exploration.</strong> This option is correct because the passage describes the Renaissance as a period that emphasized humanism and a revival of learning, which inherently fostered an environment ripe for scientific inquiry and exploration.</p> <p><strong>A: The Renaissance stifled scientific innovation due to its focus on art.</strong> This option is incorrect as the passage suggests that the flourishing of arts and sciences occurred simultaneously, rather than one hindering the other.</p> <p><strong>B: Scientific advancements were divorced from the intellectual climate of the Renaissance.</strong> This option is incorrect because the passage implies that the intellectual climate of the Renaissance, characterized by humanism, was integral to the advances in various fields, including science.</p> <p><strong>D: The Renaissance had no significant impact on science according to the passage.</strong> This option is incorrect since the passage outlines how the Renaissance's cultural movements and emphasis on learning indeed laid the groundwork for future scientific developments.</p>"}	\N
		582	4	2	Technological Innovation of the Renaissance	Which technological innovation is credited to Johannes Gutenberg that had a significant impact during the Renaissance?	-1	0	0	{}	2025-02-07 06:46:51.26	2025-02-07 06:46:51.26	t	59	\N	f	{"solution": "<p>The correct answer is:</p> <p><strong>C: The printing press.</strong> This option is correct because the passage explicitly states that Johannes Gutenberg's invention of the printing press revolutionized the dissemination of knowledge during the Renaissance, allowing ideas to spread more widely and efficiently.</p> <p><strong>A: The steam engine.</strong> This option is incorrect as the steam engine is associated with the later stages of the Industrial Revolution, not the Renaissance.</p> <p><strong>B: The spinning jenny.</strong> This option is also incorrect because the spinning jenny was an invention that emerged much later during the Industrial Revolution, significantly impacting textile production rather than the Renaissance.</p> <p><strong>D: The mechanical clock.</strong> This option is incorrect since while clocks were important for timekeeping, the passage does not attribute their invention or significance to Gutenberg or the Renaissance period specifically.</p>"}	\N
		583	4	2	Primary Purpose of the Passage on Historical Transformations	What is the primary purpose of the passage regarding transformative historical eras?	-1	0	0	{}	2025-02-07 06:46:51.278	2025-02-07 06:46:51.278	t	59	\N	f	{"solution": "<p>The correct answer is:</p> <p><strong>B: To illustrate the interconnectedness of major historical events and their impacts on society.</strong> This option is correct because the passage discusses the Renaissance, Age of Exploration, and Industrial Revolution as transformative periods that influenced each other and shaped modern society through cultural and technological advancements.</p> <p><strong>A: To highlight the negative consequences of exploration and industrialization.</strong> This option is incorrect as the passage does not solely focus on the negative consequences; it emphasizes the broader influence of these eras on progress and human experience.</p> <p><strong>C: To provide a detailed timeline of important inventions in history.</strong> This option is incorrect because the passage is not structured as a timeline or list of inventions, rather it provides a thematic discussion of historical movements.</p> <p><strong>D: To argue against the notion that art influences scientific progress.</strong> This option is incorrect since the passage supports the idea that art and science flourished together during the Renaissance, rather than opposing it.</p>"}	\N
		584	4	2	Traits of Resilience in Psychology	According to the passage, which of the following traits is commonly associated with resilient individuals?	-1	0	0	{}	2025-02-07 06:46:51.3	2025-02-07 06:46:51.3	t	60	\N	f	{"solution": "<p>The correct answer is <strong>C: Optimism</strong>. The passage explicitly states that resilient individuals often possess traits such as optimism, highlighting its importance in adapting to adverse situations.</p> <p><strong>A: Cognitive inflexibility</strong> is incorrect. The passage discusses cognitive flexibility as a trait associated with resilience, not inflexibility.</p> <p><strong>B: Pessimism</strong> is also incorrect. In contrast to optimism, pessimism would likely hinder resilience, making it an unsuitable choice.</p> <p><strong>D: Social isolation</strong> is incorrect. The passage mentions that robust social support networks are traits of resilient individuals, indicating that social isolation would not be a characteristic of resilience.</p>"}	\N
RC		809	2	1	Central Themes of the Industrial Revolution	What is the main idea of the passage regarding the Industrial Revolution?	3	0	0	{}	2025-02-08 05:11:43.33	2025-02-08 05:11:43.33	t	87	44	t	{"solution": "<p>The correct answer is <strong>C</strong>: The Industrial Revolution resulted in significant economic and social transformations.</p><p>This option captures the passage's main idea, highlighting how the Industrial Revolution brought about both economic changes—transitioning to factory production—and social issues such as the rise of the working class and the need for labor rights.</p><p><strong>A</strong>: The Industrial Revolution led to changes solely in economic practices is incorrect because the passage emphasizes social and environmental impacts as well.</p><p><strong>B</strong>: The Industrial Revolution was a period of social progress with no negative effects is wrong; the passage clearly notes the adverse conditions that accompanied industrial growth.</p><p><strong>D</strong>: The Industrial Revolution primarily affected rural communities is misleading; the transformation was centered in urban areas where people moved for work, thus affecting urban communities much more significantly.</p>"}	8
		585	4	2	Implications of Technology on Mental Health	What can be inferred about the relationship between technology and mental health based on the passage?	-1	0	0	{}	2025-02-07 06:46:51.348	2025-02-07 06:46:51.348	t	60	\N	f	{"solution": "<p>The correct answer is <strong>A: Technology can improve access to mental health services for a wider audience.</strong> The passage highlights how digital mental health tools offer accessibility and convenience, suggesting a positive relationship between technology and access to mental health services.</p> <p><strong>B: All digital mental health tools are considered effective and reliable.</strong> This option is incorrect as the passage raises questions about efficacy and potential drawbacks of these tools, indicating that not all are guaranteed to be effective.</p> <p><strong>C: The use of technology in psychology eliminates the need for human therapists.</strong> This statement is incorrect. The passage discusses the role of technology but also emphasizes the importance of human empathy in psychological interventions, indicating that therapists still have a vital role.</p> <p><strong>D: Privacy concerns regarding digital tools are unfounded and negligible.</strong> This is not supported by the passage; rather, it states that privacy concerns are a significant issue that needs consideration, making this option incorrect.</p>"}	\N
		586	4	2	Key Psychological Treatment Approaches	What psychological treatment approach is mentioned in the passage as an example of a paradigm shift?	-1	0	0	{}	2025-02-07 06:46:51.366	2025-02-07 06:46:51.366	t	60	\N	f	{"solution": "<p>The correct answer is <strong>A: Cognitive-Behavioral Therapy</strong>. The passage explicitly mentions this approach as an example of a paradigm shift in psychological treatment, highlighting its emphasis on the interconnectedness of thought patterns, emotions, and behaviors.</p> <p><strong>B: Psychoanalysis</strong> is incorrect. The passage does not mention psychoanalysis as an example of a recent shift in treatment approaches.</p> <p><strong>C: Humanistic Therapy</strong> is also incorrect. This approach is not referenced in the passage as a paradigm shift, so it does not fit the context.</p> <p><strong>D: Gestalt Therapy</strong> is incorrect as well. Similar to the previous options, gestalt therapy is not mentioned in the passage, making it an unsuitable answer.</p>"}	\N
GI	GI - <Finance> - <Critical Thinking> - <Pie Chart> - <difficulty_level: 1>	587	5	2	Budget Allocation Percentages for Departments	The organization allocated __________% of its budget to Research and Development, while __________% was allocated to Operations.	1	0	0	[{"data": [{"label": "Marketing", "value": 25}, {"label": "Research and Development", "value": 35}, {"label": "Human Resources", "value": 20}, {"label": "Operations", "value": 15}, {"label": "IT", "value": 5}], "graph": "pie chart", "title": "Budget Allocation for 2023", "description": "This pie chart illustrates the distribution of an organization's budget for the year 2023 across various departments."}]	2025-02-07 06:46:51.385	2025-02-07 06:46:51.385	f	\N	\N	f	{"solution": "To find the percentages allocated to Research and Development and Operations, we can directly refer to the pie chart data: \\n\\n- The percentage allocated to Research and Development is given as 35\\\\%. \\n- The percentage allocated to Operations is given as 15\\\\%. \\n\\nThus, the answers are: 35\\\\% for Research and Development and 15\\\\% for Operations."}	\N
TA	TA - <Resource Management> - <Comparative Analysis> - <Simple Table> - <Inferred/Conflicting type> - <difficulty_level: 2>	588	5	2	Efficiency Comparison of Resource Allocation across Departments	The table presents the allocation of resources among various departments within a company, highlighting both the percentage of resources allocated and necessary, along with efficiency ratios and performance outcomes. Based on this information, can we infer that the Sales department operates with the highest efficiency ratio compared to the other departments?	2	0	0	{"tables": [{"data": [[30, 25, 20, 15, 5, 5], [25, 30, 25, 10, 5, 5], [1.2, 0.83, 0.8, 1.5, 1, 1], [30000, 25000, 20000, 15000, 5000, 5000], ["Good", "Average", "Average", "Excellent", "Poor", "Poor"]], "rows": ["Row1", "Row2", "Row3", "Row4", "Row5", "Row6"], "columns": [{"Department": ["HR", "Finance", "IT", "Sales", "Marketing", "Operations"]}, {"Resources Allocated (in %)": ["30", "25", "20", "15", "5", "5"]}, {"Resources Needed (in %)": ["25", "30", "25", "10", "5", "5"]}, {"Efficiency Ratio": ["1.2", "0.83", "0.8", "1.5", "1", "1"]}, {"Budget Utilization (in $)": ["30000", "25000", "20000", "15000", "5000", "5000"]}, {"Performance Outcome": ["Good", "Average", "Average", "Excellent", "Poor", "Poor"]}], "table_name": "Resource Allocation Comparison"}]}	2025-02-07 06:46:51.413	2025-02-07 06:46:51.413	f	\N	\N	f	["Option A is incorrect because the Sales department has an efficiency ratio of 1.5, which is actually the highest among all departments.", "Option B is correct as the IT department's efficiency ratio is 0.8, which is lower than Sales but higher than others like Finance and Marketing.", "Option C is incorrect because while the Operations department has an efficiency ratio of 1, it is not close to the Sales department's efficiency ratio of 1.5."]	\N
GI	GI - <Strategy and Management> - <Synthesis of Information> - <Pie Chart> - <difficulty_level: 1>	589	5	2	Budget Allocation Comparison Between Departments	The budget allocated to __________ Marketing is greater than the amount allocated to __________ Human Resources.	1	0	0	[{"data": [{"label": "Marketing", "value": 35}, {"label": "Research & Development", "value": 25}, {"label": "Operations", "value": 20}, {"label": "Human Resources", "value": 10}, {"label": "Sales", "value": 10}], "graph": "pie chart", "title": "Budget Allocation by Department", "description": "This pie chart represents the distribution of the annual budget across various departments within the organization."}]	2025-02-07 06:46:51.439	2025-02-07 06:46:51.439	f	\N	\N	f	{"solution": "To find the budget allocated to Marketing and Human Resources from the pie chart data, we note that the values are as follows: \\\\text{Marketing} = 35\\\\% \\\\text{ and } \\\\text{Human Resources} = 10\\\\%. Thus, we fill in the blanks with the corresponding values. The completed sentence is: The budget allocated to \\\\text{Marketing} is greater than the amount allocated to \\\\text{Human Resources}."}	\N
GI	GI - <Marketing and Sales> - <Quantitative Reasoning> - <Bar Chart> - <difficulty_level: 1>	590	5	2	Comparison of Product A and Product B Sales in Q1	In Q1, the sales of ___________ were ___________ more than the sales of Product B.	1	0	0	[{"data": [{"Q1": 1000, "Q2": 1200, "Q3": 1500, "Q4": 1700, "category": "Product A"}, {"Q1": 800, "Q2": 950, "Q3": 1100, "Q4": 1300, "category": "Product B"}, {"Q1": 600, "Q2": 750, "Q3": 900, "Q4": 1050, "category": "Product C"}], "graph": "bar chart", "title": "Quarterly Sales Data", "x-axis": "Products", "y-axis": "Sales (in USD)", "description": "This chart displays the sales figures of different products over four quarters."}]	2025-02-07 06:46:51.465	2025-02-07 06:46:51.465	f	\N	\N	f	{"solution": "To find the sales of Product A and Product B in Q1:\\n\\n- Sales of Product A in Q1 = \\\\$1000\\n- Sales of Product B in Q1 = \\\\$800\\n\\nNow, we calculate the difference:\\n\\nDifference = Sales of Product A - Sales of Product B = \\\\$1000 - \\\\$800 = \\\\$200\\n\\nThus, the sales of Product A were \\\\$200 more than the sales of Product B."}	\N
GI	GI - <Economics> - <Synthesis of Information> - <Stacked Bar Chart> - <difficulty_level: 2>	591	5	2	Quarterly Revenue Analysis of Product Lines	The total revenue for Q3 is ___________ and for Q4 is ___________.	2	0	0	[{"data": [{"values": [{"value": 5000, "region": "Product A"}, {"value": 3000, "region": "Product B"}, {"value": 2000, "region": "Product C"}], "category": "Q1"}, {"values": [{"value": 6000, "region": "Product A"}, {"value": 4000, "region": "Product B"}, {"value": 3500, "region": "Product C"}], "category": "Q2"}, {"values": [{"value": 8000, "region": "Product A"}, {"value": 5000, "region": "Product B"}, {"value": 4500, "region": "Product C"}], "category": "Q3"}, {"values": [{"value": 9000, "region": "Product A"}, {"value": 5500, "region": "Product B"}, {"value": 5000, "region": "Product C"}], "category": "Q4"}], "graph": "stacked bar chart", "title": "Quarterly Revenue by Product Lines", "x-axis": "Quarters", "y-axis": "Revenue (in USD)", "description": "This chart shows the breakdown of total revenue by different product lines for each quarter."}]	2025-02-07 06:46:51.49	2025-02-07 06:46:51.49	f	\N	\N	f	{"solution": "To find the total revenue for each quarter, we can sum the revenue from all product lines for the specified quarters.\\n\\n1. For Q3:\\n   Total Revenue Q3 = \\text{Revenue of Product A} + \\text{Revenue of Product B} + \\text{Revenue of Product C}\\n   \\\\\\\\;\\n   Total Revenue Q3 = 8000 + 5000 + 4500 = 17500 \\\\\\text{ (in USD)}\\n\\n2. For Q4:\\n   Total Revenue Q4 = \\text{Revenue of Product A} + \\text{Revenue of Product B} + \\text{Revenue of Product C}\\n   \\\\\\\\;\\n   Total Revenue Q4 = 9000 + 5500 + 5000 = 19500 \\\\\\text{ (in USD)}\\n\\nTherefore, the total revenue for Q3 is 17500 and for Q4 is 19500."}	\N
		592	5	2		Based on the Quarterly Sales Data provided, which product had the highest total sales over the four quarters?	1	0	0	{}	2025-02-07 06:46:51.52	2025-02-07 06:46:51.52	t	61	\N	f	{"solution": "The passage discusses how logistics and supply chain companies are adopting technology while considering the associated risks and workforce implications. A critical aspect is how companies can balance technology integration and workforce development. A well-managed transition can yield benefits, while a poorly managed one could cause disruptions. Therefore, the best approach involves understanding both the technological needs and the workforce requirements."}	\N
		593	5	2		Based on the data presented, what is the total sales amount for Product C across all four quarters?	2	0	0	{}	2025-02-07 06:46:51.543	2025-02-07 06:46:51.543	t	61	\N	f	{"solution": "The passage emphasizes the need for companies to adopt a holistic approach when integrating technology into their logistics and supply chain practices. This includes understanding the risks associated with automation and ensuring workforce development to mitigate job displacement. Companies should invest not only in technology but also in training programs for their employees to equip them for new roles. This balanced strategy can help organizations remain competitive while protecting their workforce."}	\N
TA	TA - <Business> - <Critical Reasoning> - <Simple Table> - <Inferred/Conflicting type> - <difficulty_level: 1>	594	5	2	Analysis of Regional Market Share in Product Sales	The table displays the sales data for Product A and Product B across various regions along with the total sales, market share, and growth rate. Based on the sales information, can we conclude which region has the highest market share?	1	0	0	{"tables": [{"data": [[2000, 1500, 3500, 30, 10], [3000, 2000, 5000, 25, 20], [1500, 2500, 4000, 20, 15], [4000, 1000, 5000, 35, 5], [1600, 2400, 4000, 10, 25], [2500, 3000, 5500, 15, 12]], "rows": ["North", "South", "East", "West", "Central", "Northeast"], "columns": ["Region", "Product A Sales", "Product B Sales", "Total Sales", "Market Share (%)", "Growth Rate (%)"], "table_name": "Product Sales by Region"}]}	2025-02-07 06:46:51.563	2025-02-07 06:46:51.563	f	\N	\N	f	["Option A is incorrect because the North region has a market share of 30%, which is not the highest among the regions listed.", "Option B is correct as the South region has a market share of 25%, which, relative to the other regions, is the highest available in the provided data.", "Option C is incorrect because while the West region has a market share of 35%, it is possible that it is inaccurately represented as it should be lower than what we observe in the South region."]	\N
GI	GI - <Economics> - <Pattern Recognition> - <Scatter Plot> - <difficulty_level: 4>	595	5	2	Analyzing Advertising Spend and Sales Revenue Correlation	Based on the scatter plot above, when the advertising spend reaches ___________ USD, the sales revenue is predicted to be ___________ USD.	4	0	0	[{"data": [{"x": 5000, "y": 20000, "label": "Product A"}, {"x": 7000, "y": 30000, "label": "Product B"}, {"x": 4000, "y": 15000, "label": "Product C"}, {"x": 10000, "y": 40000, "label": "Product D"}, {"x": 6000, "y": 25000, "label": "Product E"}], "graph": "scatter plot", "title": "Advertising Spend vs. Sales Revenue", "x-axis": "Advertising Spend (in USD)", "y-axis": "Sales Revenue (in USD)", "description": "This graph illustrates the relationship between advertising spend and corresponding sales revenue for various products."}, {"data": [{"series": "Product A", "values": [{"x": "January", "y": 5000}, {"x": "February", "y": 7000}, {"x": "March", "y": 8000}, {"x": "April", "y": 6000}, {"x": "May", "y": 9000}, {"x": "June", "y": 10000}]}, {"series": "Product B", "values": [{"x": "January", "y": 3000}, {"x": "February", "y": 4000}, {"x": "March", "y": 5000}, {"x": "April", "y": 3500}, {"x": "May", "y": 6000}, {"x": "June", "y": 8000}]}], "graph": "line chart", "title": "Sales Revenue Over Time", "x-axis": "Months", "y-axis": "Sales Revenue (in USD)", "description": "This line chart shows the monthly sales revenue trends for the products over a six-month period."}]	2025-02-07 06:46:51.589	2025-02-07 06:46:51.589	f	\N	\N	f	{"solution": "To solve the question, we will analyze the data from the scatter plot. We can observe the trend to identify the points that relate advertising spend to sales revenue. \\\\n\\\\nLet's calculate the predicted sales revenue when the advertising spend is \\\\$7000. Using the relation from the scatter plot: \\\\n\\\\nFor advertising spend \\\\$7000, sales revenue is approximately \\\\$30000 derived from the data points shown in the graph.\\\\n\\\\nThus, we fill in the blanks as follows:\\\\n\\\\n1. Advertising Spend = 7000 USD\\\\n2. Sales Revenue = 30000 USD\\\\n\\\\nHence the complete statement becomes: Based on the scatter plot above, when the advertising spend reaches \\\\$7000 USD, the sales revenue is predicted to be \\\\$30000 USD."}	\N
GI	GI - <Economics> - <Quantitative Reasoning> - <Line Chart> - <difficulty_level: 1>	596	5	2	Inflation Rate Changes from 2021 to 2022	The inflation rate in 2021 was __________ while the inflation rate in 2022 increased to __________.	1	0	0	[{"data": [{"series": "Inflation Rate", "values": [{"x": "2018", "y": 2.1}, {"x": "2019", "y": 1.8}, {"x": "2020", "y": 1.2}, {"x": "2021", "y": 4.7}, {"x": "2022", "y": 7.0}]}], "graph": "line chart", "title": "Annual Inflation Rate Over Five Years", "x-axis": "Years", "y-axis": "Inflation Rate (%)", "description": "This chart shows the changes in annual inflation rates from 2018 to 2022."}]	2025-02-07 06:46:51.616	2025-02-07 06:46:51.616	f	\N	\N	f	{"solution": "From the line chart, the inflation rate in 2021 is 4.7\\\\% and the inflation rate in 2022 increased to 7.0\\\\%. Therefore, we can write: \\\\text{Inflation Rate in 2021} = 4.7\\\\% \\\\text{ and } \\\\text{Inflation Rate in 2022} = 7.0\\\\%."}	\N
GI	GI - <Budget> - <Attention to Detail> - <Line Chart> - <difficulty_level: 2>	597	5	2	Budget Allocation Trends in Marketing Over Four Years	Based on the line chart, the budget allocation for Digital Marketing in 2022 was ___________ and for TV Advertising in 2023 was ___________.	2	0	0	[{"data": [{"series": "Digital Marketing", "values": [{"x": "2020", "y": 30000}, {"x": "2021", "y": 40000}, {"x": "2022", "y": 50000}, {"x": "2023", "y": 65000}]}, {"series": "TV Advertising", "values": [{"x": "2020", "y": 20000}, {"x": "2021", "y": 25000}, {"x": "2022", "y": 30000}, {"x": "2023", "y": 40000}]}, {"series": "Print Advertising", "values": [{"x": "2020", "y": 15000}, {"x": "2021", "y": 10000}, {"x": "2022", "y": 8000}, {"x": "2023", "y": 5000}]}], "graph": "line chart", "title": "Annual Marketing Budget Allocation Over Time", "x-axis": "Years", "y-axis": "Budget Allocation (in USD)", "description": "This chart illustrates the trend of marketing budget allocation over four consecutive years."}]	2025-02-07 06:46:51.642	2025-02-07 06:46:51.642	f	\N	\N	f	{"solution": "To find the budget allocation for Digital Marketing in 2022 and TV Advertising in 2023, we can refer directly to the values indicated in the line chart. \\\\\\\\text{From the chart:} \\\\\\\\text{Digital Marketing in 2022: } 50000 \\\\\\\\text{TV Advertising in 2023: } 40000. \\\\\\\\text{Thus the values are: } 50000 \\\\text{ and } 40000."}	\N
TA	TA - <Marketing and Sales> - <Data Synthesis> - <Simple Table> - <Acceptable/Not Acceptable type> - <difficulty_level: 2>	598	5	2	Assessment of Sales Performance in the South Region	The table above displays the sales performance by region for each quarter in a year, along with the total sales and the corresponding performance rating (Acceptable/Not Acceptable). Based on the data provided, can we determine if the sales performance in the South region is acceptable based on the total sales figures?	2	0	0	{"tables": [{"data": [[15000, 18000, 21000, 24000, 78000, "Acceptable"], [12000, 15000, 19000, 20000, 66000, "Not Acceptable"], [9000, 11000, 13000, 14000, 49000, "Acceptable"], [16000, 17000, 22000, 25000, 80000, "Acceptable"], [11000, 14000, 16000, 17000, 60000, "Not Acceptable"]], "rows": ["North", "South", "East", "West", "Central"], "columns": [{"Region": ["North", "South", "East", "West", "Central"]}, {"Q1 Sales ($)": [15000, 12000, 9000, 16000, 11000]}, {"Q2 Sales ($)": [18000, 15000, 11000, 17000, 14000]}, {"Q3 Sales ($)": [21000, 19000, 13000, 22000, 16000]}, {"Q4 Sales ($)": [24000, 20000, 14000, 25000, 17000]}, {"Total Sales ($)": [78000, 66000, 49000, 80000, 60000]}, {"Performance Rating": ["Acceptable", "Not Acceptable", "Acceptable", "Acceptable", "Not Acceptable"]}], "table_name": "Marketing and Sales Performance"}]}	2025-02-07 06:46:51.669	2025-02-07 06:46:51.669	f	\N	\N	f	["Option A is 'No' because the total sales in the South region amount to \\\\$66,000, which aligns with the 'Not Acceptable' performance rating indicated in the table.", "Option B is 'Yes' as the total sales figure of \\\\$66,000 for the South region is explicitly marked as 'Not Acceptable' in the performance rating column.", "Option C is 'No' since the performance rating for the South region is 'Not Acceptable', contrary to what this option suggests."]	\N
Data Sufficiency	DS - <Data Sufficiency> - <Critical Reasoning> - <difficulty_level: 1>	599	5	2	Impact of Price Increase on Revenue in a Retail Store	Based on the statements above, can we conclusively determine whether increasing the price per item will always result in increased total revenue?	1	0	0	{"passages": "In a certain retail store, the relationship between the number of items sold (S) and the total revenue generated (R) is governed by the equation R = pS, where p is the price per item. The store owner wants to determine whether increasing the price per item will lead to a proportional increase in total revenue, given that sales data over the past year showed fluctuations caused by seasonal demand changes.", "statements": ["Statement 1: During the summer months, the average price per item sold was $15, while a promotional discount resulted in sales increasing by 30%.", "Statement 2: In the autumn season, the price per item was raised to $20, yet the number of items sold decreased by 25% compared to the previous season."]}	2025-02-07 06:46:51.695	2025-02-07 06:46:51.695	f	\N	\N	f	{"solution": "The statements provide information about price changes and their effects on sales but do not establish a definitive relationship between price increases and total revenue across all seasons. Therefore, while individual scenarios are discussed, we cannot conclude universally that increased prices will always result in higher revenue."}	\N
Data Sufficiency	DS - <Arithmetic> - <Logical Reasoning> - <difficulty_level: 5>	600	5	2	Maximizing Gadget Production Capacity in a Factory Setup	Is it possible for the production capacity of gadgets to exceed 30 units on any given day based on the above statements?	5	0	0	{"passages": "A certain factory produces widgets and gadgets. The production capacity for widgets is given by the equation W = 3X + 7, where X is the number of machines dedicated to widget production. Gadgets are produced using the same machines, but the efficiency decreases based on the equation G = 2(X - 5). Given that the total production of widgets and gadgets is limited to a maximum of 100 units per day, can you determine if the production capacity of gadgets can exceed 30 units on any given day?", "statements": ["Statement (1): The factory has a total of 10 machines available for production.", "Statement (2): On a specific day, the factory produced 50 widgets."]}	2025-02-07 06:46:51.711	2025-02-07 06:46:51.711	f	\N	\N	f	{"solution": "By analyzing Statement (1), if there are 10 machines, W can be calculated as W = 3(10) + 7 = 37, leaving G = 100 - 37 = 63, which exceeds 30. Statement (2) indicates that 50 widgets were produced, hence G = 100 - 50 = 50, which also exceeds 30. Both statements alone suffice to confirm that gadget production can exceed 30 units independently."}	\N
Data Sufficiency	DS - <Word Problems> - <Logical Reasoning> - <difficulty_level: 1>	601	5	2	Workforce Increase and Productivity Relationship	Based on the statements above, can you determine if a 10% productivity increase is achievable solely through a workforce increase?	1	0	0	{"passages": "A company plans to increase its workforce by a certain percentage over the next year. Currently, the company employs 250 workers. The management anticipates that the percentage increase will directly affect productivity, but they are uncertain of the exact relationship between the increase in workforce and the anticipated output. Consequently, they have made plans to either hire additional workers or increase the productivity of current workers. The question remains: what percentage increase in workforce is necessary for the company to achieve an overall productivity increase of at least 10%?", "statements": ["Statement 1: If the workforce is increased by 30%, the productivity of the company is expected to increase by 12%.", "Statement 2: The total productivity of the current workforce, when evaluated over a specific time frame, has historically increased by an average of 8% with a 25% increase in workforce."]}	2025-02-07 06:46:51.728	2025-02-07 06:46:51.728	f	\N	\N	f	{"solution": "Statement 1 alone provides a direct correlation between the percentage increase in workforce and the productivity increase, confirming that a 30% increase in workforce leads to a 12% productivity increase, which covers the company's target of at least 10%. Statement 2, while informative about productivity trends, does not guarantee a solution to the specific inquiry regarding achieving a 10% productivity increase based solely on the given workforce percentage. Therefore, Statement 1 alone is sufficient to determine the answer."}	\N
Data Sufficiency	DS - <Data Sufficiency> - <Efficiency and Time Management> - <difficulty_level: 3>	602	5	2	Retailer Sales Volume Comparison	Is the retailer's total sales volume this year greater than the total sales volume last year?	3	0	0	{"passages": "A certain retailer operates several stores across different states, each with varying sales volumes. The store located in State A has reported a 15% increase in sales over the previous year, while the store in State B has seen a decrease in sales by 10%. The regional manager is interested in determining whether the total sales volume for the retailer this year exceeds the total sales volume from last year across all states.", "statements": ["The sales volume of the store in State A last year was $200,000.", "The total sales volume of the stores in State B and C combined last year was $150,000 and the store in State C has a reported increase of 20%."]}	2025-02-07 06:46:51.744	2025-02-07 06:46:51.744	f	\N	\N	f	{"solution": "Statement (1) alone allows us to calculate the sales volume for State A this year, but without knowing the sales volumes for State B and C or any specific totals, we cannot determine the overall sales volume. Statement (2) provides information about State B and C, but without the specific sales volume from State A or the overall sales volume from last year, we still cannot definitively answer the question. However, combining both statements lets us calculate necessary comparisons of sales volumes, leading to the conclusion about total sales volumes."}	\N
Data Sufficiency	DS - <Data Sufficiency> - <Critical Reasoning> - <difficulty_level: 1>	603	5	2	Equal Funding Distribution for School Science Fair Projects	Is it possible for each student to receive an equal amount of funding for their project if the school has a \\$5,000 budget?	1	0	0	{"passages": "A certain school organizes an annual science fair where students present their projects. Each project requires a specific budget to cover materials, equipment, and other costs. This year's fair is projected to host a maximum of 20 projects. However, the school has a limited budget of \\\\$5,000 for all projects combined. The goal is to determine whether it is feasible for each student to receive an equal amount of funding while adhering to the project's budget constraints.", "statements": ["Statement (1): The average cost per project is estimated to be \\\\$250.", "Statement (2): The school plans to cut down the maximum number of projects to 15."]}	2025-02-07 06:46:51.761	2025-02-07 06:46:51.761	f	\N	\N	f	{"solution": "Both statements indicate how the total budget can be allocated across a varying number of projects. Statement (1) shows that with 20 projects, the funding per project would be \\\\$250, which fits perfectly into the \\\\$5,000 budget. However, statement (2) modifies the situation by reducing the number of projects to 15, where each student would then receive \\\\$333.33, exceeding the budget. Therefore, both statements together affirm that the funding can be equalized, but neither statement alone conclusively determines the feasibility of equal funding under the budget constraints."}	\N
Data Sufficiency	DS - <Data Sufficiency> - <Critical Reasoning> - <difficulty_level: 3>	604	5	2	Determining Bicycle Sales Based on Production and Price	What information is sufficient to determine the number of bicycles sold in the town last month?	3	0	0	{"passages": "In a certain town, the number of bicycles sold in one month (B) is directly proportional to the number of bikes produced (P) in that month and inversely proportional to the average price of each bicycle (A). Accordingly, the relationship can be expressed as B = k * (P/A) where k is a constant. Additionally, it is known that in the last year, the average price of bicycles varied significantly due to market fluctuations. The town council is now interested in determining how many bicycles were sold last month.", "statements": ["Statement (1): The town produced 500 bicycles last month.", "Statement (2): The average price of each bicycle last month was $200."]}	2025-02-07 06:46:51.777	2025-02-07 06:46:51.777	f	\N	\N	f	{"solution": "Both statements together provide a complete picture needed to determine the total bicycles sold, as they give both the production and pricing context, which is crucial given the relationship B = k * (P/A). Alone, neither statement directly provides sufficient information to calculate B."}	\N
Data Sufficiency	DS - <Data Sufficiency> - <Attention to Detail> - <difficulty_level: 2>	605	5	2	Maximizing Production of Type A Gadgets under Constraints	Is it possible for the factory to produce the maximum number of Type A gadgets while meeting both the work hour and type production requirements?	2	0	0	{"passages": "A factory produces two types of gadgets: Type A and Type B. Each Type A gadget requires 3 hours of work and each Type B gadget requires 2 hours of work. The factory has a total of 120 hours available for production in a week. Additionally, there is a rule that at least twice as many Type A gadgets must be produced as Type B gadgets. How many Type A gadgets can the factory produce in a week if these conditions are to be met?", "statements": ["Statement (1): The factory can produce a maximum of 30 Type A gadgets.", "Statement (2): The factory can produce a maximum of 20 Type B gadgets."]}	2025-02-07 06:46:51.794	2025-02-07 06:46:51.794	f	\N	\N	f	{"solution": "Both statements together provide essential information regarding the maximum number of Type A and Type B gadgets that can be produced. Statement (1) indicates that the factory can produce up to 30 Type A gadgets, while Statement (2) indicates that the factory can produce up to 20 Type B gadgets. Using both statements, we can verify whether these quantities meet the production rules (i.e., at least twice as many Type A as Type B) and the total hours available. The calculations confirm that both conditions can be satisfied simultaneously. Therefore, the correct option is C."}	\N
Data Sufficiency	DS - <Algebra> - <Critical Reasoning> - <difficulty_level: 1>	606	5	2	Determining Value of z from Algebraic Expressions	Can the exact value of z be determined from the above statements?	1	0	0	{"passages": "In a certain algebraic expression, let x represent a positive integer and y represent the product of x and two additional consecutive integers. The relationship between x and y is defined by the equation y = x(x + 1)(x + 2). A third integer z is introduced, which is defined as the sum of x, y, and 5. It is necessary to ascertain the specific value of z based solely on the conditions described.", "statements": ["Statement (1): x is equal to 3.", "Statement (2): The result of y when x is 3 leads to z being an even number."]}	2025-02-07 06:46:51.811	2025-02-07 06:46:51.811	f	\N	\N	f	{"solution": "From Statement (1), we have x = 3. Substituting this value into the equation for y gives y = 3(3 + 1)(3 + 2) = 3 * 4 * 5 = 60. Then, z = x + y + 5 = 3 + 60 + 5 = 68. Therefore, Statement (1) alone is sufficient to determine z. Statement (2) states that y leads to z being an even number, but does not provide the necessary value of x or its relation to z directly. Hence, Statement (2) alone is insufficient. Thus, the answer is A: Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient."}	\N
	ChildQuestion: 1 <Critical Reasoning> - <Dicotomous Choice(Acceptable/Not Acceptable)> - <2>	607	5	2	Evaluating the Relationship Between Logistics Costs and Supply Chain Efficiency	Is it acceptable to conclude that higher logistics costs universally lead to lower supply chain efficiency based on the provided data?	2	0	0	{}	2025-02-07 06:46:51.832	2025-02-07 06:46:51.832	t	62	\N	f	{"solution": "To determine if it is acceptable to conclude that higher logistics costs lead to lower supply chain efficiency, we analyze the following: \\n\\nFrom the scatter plot illustrating logistics costs versus supply chain efficiency, we observe varying data points. For example, Company A incurs logistics costs of \\\\$20000 and has a supply chain efficiency of 80\\\\%. In contrast, Company D has higher logistics costs of \\\\$40000 but lower efficiency at 60\\\\%. This suggests some correlation between higher costs leading to lower efficiency. \\n\\nHowever, Company C demonstrates that lower logistics costs of \\\\$15000 coincide with higher efficiency at 90\\\\%. Thus, there are exceptions to the correlation.  \\n\\nAdditionally, the passage indicates that logistics costs can be managed effectively, impacting efficiency positively through optimization strategies. Therefore, while there is evidence supporting a relationship, it does not universally apply to all cases, leading us to conclude that it is **Not Acceptable** to generalize this finding without further evidence for each specific situation. \\n\\nIn summary, conclusions drawn from the data must consider individual company practices and strategies, highlighting the complexity of the logistics cost-efficiency dynamic."}	\N
	ChildQuestion: 2 <Synthesis> - <Dicotomous Choice(Yes/No)> - <1>	608	5	2	Inferring the Impact of Logistics Cost Management on Supply Chain Efficiency	Can it be inferred that effective management of logistics costs positively influences supply chain efficiency based on the combined information from the passages and charts?	1	0	0	{}	2025-02-07 06:46:51.856	2025-02-07 06:46:51.856	t	62	\N	f	{"solution": "To analyze the possibility that effective management of logistics costs positively influences supply chain efficiency, we reference both the passage and the visual data sources. \\n\\nThe passage highlights the significance of managing logistics costs through strategies such as advanced forecasting tools and efficient routing. It states that effective management is crucial for minimizing costs while maximizing supply chain operations.\\n\\nLooking at the provided scatter plot data, we note that Company C, with the lowest logistics costs of \\\\$15000, boasts the highest supply chain efficiency at 90\\\\%. This suggests that lower logistics costs, potentially achieved through effective management, may correlate with higher efficiency in operational practices. \\n\\nAdditionally, the line chart data supports this notion, showing that as companies implement better management practices, trends indicate fluctuations in logistics costs can lead to stable or improved efficiency.\\n\\nThus, we can logically synthesize the information across the sources, concluding that effective management of logistics costs does indeed appear to positively influence supply chain efficiency.\\n\\nTherefore, the answer is **Yes**, effective management of logistics costs correlates with improvements in supply chain efficiency."}	\N
TC-2	<Psychology> - <TC-2> - <difficulty-level: 2> - <vocabulary-level:1>	788	2	1	Psychology and Incongruent Behaviors	The study of psychology often reveals that individuals exhibit _______ behaviors that may seem incongruent with their conscious thoughts, suggesting a deeper _______ at play within the cognitive processes.	2	0	0	{}	2025-02-08 05:11:42.688	2025-02-08 05:11:42.688	f	\N	43	t	{"solution": "<p>The correct options are <b>multifaceted</b> and <b>cognitive dissonance</b>. These choices indicate that behaviors can be complex and influenced by deeper psychological conflicts.</p><p>Option Discussion:</p><ul><li><b>Option A: multifaceted</b> - This describes behaviors that are intricate and varied, fitting the context.</li><li><b>Option B: erratic</b> - While this indicates inconsistent behaviors, it does not capture the underlying complexity.</li><li><b>Option C: anomalous</b> - This refers to behaviors that are abnormal but lacks the explanation of cognitive processes.</li><li><b>Option D: consistent</b> - This contradicts the idea of incongruent behaviors.</li></ul><p>For the second blank:</p><ul><li><b>Option E: conflict</b> - Could imply a struggle but lacks specificity in cognitive terms.</li><li><b>Option F: strategy</b> - Not relevant to the concept of underlying psychological processes.</li><li><b>Option G: cognitive dissonance</b> - This perfectly explains the psychological conflict arising from incongruent beliefs and behaviors.</li><li><b>Option H: harmony</b> - This contradicts the idea of incongruence altogether.</li></ul>"}	1
SE	<Literature> - <SE> - <difficulty-level: 5> - <vocabulary-level:1>	789	2	1	Literary Themes of Isolation and Despair	In exploring the themes of isolation and despair, the author presents a character whose life is marked by a profound sense of _______. This feeling is particularly palpable in the later chapters, as the character grapples with their internal struggles and seeks solace in _______.	5	0	0	{}	2025-02-08 05:11:42.721	2025-02-08 05:11:42.721	f	\N	43	t	{"solution": "<p><strong>Option B: loneliness</strong> is the correct choice as it directly relates to the themes of isolation and despair the author explores—indicating the character's profound feelings in the narrative.<br> <br> <strong>Option E: companionship</strong> is also correct, as the character seeks solace in relationships, contrasting with their loneliness. <br> <br> The other options do not appropriately capture the essence of despair and isolation:<br>  <ul><li><strong>Option A: joy</strong> contradicts the themes portrayed in the text.</li><li><strong>Option C: contentment</strong> suggests a sense of satisfaction, which is not reflective of the character's struggles.</li><li><strong>Option D: betrayal</strong> does not directly connect to the overarching themes of isolation.</li><li><strong>Option F: solitude</strong> could imply a peacefulness rather than the despair the character endures.</li></ul></p>"}	2
SE	<Economics> - <SE> - <difficulty-level: 2> - <vocabulary-level:2>	790	2	1	The Dual Nature of Inflation in Economic Contexts	Although typically seen as a symptom of economic downturn, inflation can sometimes be viewed as a __________ factor that encourages spending. This explains why some economists deem a moderate level of inflation as beneficial to the economy, suggesting that a strong albeit controlled increase in prices can be __________ in promoting growth.	2	0	0	{}	2025-02-08 05:11:42.75	2025-02-08 05:11:42.75	f	\N	43	t	{"solution": "<p>In this sentence, the correct options are <b>catalytic</b> and <b>neutral</b>. The term <b>catalytic</b> suggests that inflation can act as a driving force that stimulates spending and economic activity, while <b>neutral</b> implies that inflation does not have a significant effect on economic behavior, aligning with the idea that moderate inflation can be beneficial.</p><p>Other options:</p><ul><li><b>volatile</b>: This suggests instability, which does not align with the context of promoting positive economic behavior.</li><li><b>constraining</b>: Implies restriction, contrary to the phrase encouraging spending.</li><li><b>detrimental</b>: Indicates harm, which does not fit with the view of inflation as sometimes beneficial.</li><li><b>problematic</b>: Suggests issues or difficulties, again not consistent with the positive aspects of mild inflation.</li></ul>"}	3
MCQ-Single	<Real Contextual> - <Algebra> - <Backsolving> - <Algebraic Equations> - <difficulty_level: 1>	609	3	2	Chocolate Cake Sales in Quantopia Bakery	In a recent survey conducted in the small town of Quantopia, the local bakery reported that the number of chocolate cakes sold in the morning is equal to twice the number of vanilla cakes sold. If the bakery sold a total of 30 cakes in the morning, how many chocolate cakes did they sell?	1	0	0	{}	2025-02-07 06:47:24.416	2025-02-07 06:47:24.416	f	\N	\N	f	{"solution": "<p>Let:</p>\\n<p>x = \\\\text{number of vanilla cakes sold}</p>\\n<p>Then, the number of chocolate cakes sold = 2x.</p>\\n<p>We can write the equation:</p>\\n<p>x + 2x = 30</p>\\n<p>3x = 30</p>\\n<p>x = \\\\frac{30}{3} = 10</p>\\n<p>Thus, the number of chocolate cakes sold is:</p>\\n<p>2x = 2 \\\\times 10 = 20</p>\\n<p>Therefore, the bakery sold 20 chocolate cakes in the morning.</p>"}	\N
MCQ-Single	<Real Contextual> - <Word Problems> - <Assessing given Situation(checking the ability of accessing a given situation)> - <Percentages> - <Accounting> - <difficulty_level: 1>	610	3	2	Calculating Savings from Seasonal Discounts at a Local Bakery	In a quaint little town, a local bakery known for its delicious pastries has decided to offer a seasonal discount of 20\\% on all items to attract customers. If a customer purchases a dozen croissants priced at \\$5 each, how much money does the customer save due to the discount? Calculate the total cost of the croissants before and after applying the discount to determine the savings. What is the total amount saved?	1	0	0	{}	2025-02-07 06:47:24.453	2025-02-07 06:47:24.453	f	\N	\N	f	{"solution": "<p>The total cost of the croissants before discount is calculated as follows:</p> <p>~~\\\\text{Total Cost Before Discount} = \\\\text{Price Per Croissant} \\\\times \\\\text{Number of Croissants} = 5 \\\\times 12 = 60\\\\$~~</p> <p>The total discount applied is:</p> <p>~~\\\\text{Total Discount} = \\\\text{Total Cost Before Discount} \\\\times \\\\text{Discount Rate} = 60 \\\\times 0.20 = 12\\\\$~~</p> <p>The total cost after applying the discount becomes:</p> <p>~~\\\\text{Total Cost After Discount} = \\\\text{Total Cost Before Discount} - \\\\text{Total Discount} = 60 - 12 = 48\\\\$~~</p> <p>Thus, the total amount saved by the customer is \\\\$12.</p>"}	\N
MCQ-Single	<Pure Contextual> - <Arithmetic> - <Number Sense> - <Work and Time> - <difficulty_level: 2>	611	3	2	Community Fountain Construction: Work and Time Calculation	In a quaint village, a group of enthusiastic villagers decided to work together to build a community fountain. They estimated that the total work required to complete the fountain would take 120 hours if they all worked together continuously. However, due to unforeseen circumstances, only 6 villagers were available to work each day for the first two days. Each villager is capable of completing 1/120 of the work in one hour. After two days, 4 additional villagers joined, increasing their total number to 10. Assuming that all the villagers are equally efficient, how many more days will it take for the whole group of 10 to finish the remaining work? Please calculate the total time taken to complete the fountain in hours and then convert this into days. Note that it may require a few steps of calculation to arrive at the total number of days needed.	2	0	0	{}	2025-02-07 06:47:24.481	2025-02-07 06:47:24.481	f	\N	\N	f	{"solution": "<p>To find the solution, we begin by calculating the amount of work done by the initial group of villagers:</p>\\n\\n<p>1. Initially, 6 villagers work for 2 days (which is 48 hours) as follows:</p>\\n<p>Work done by 6 villagers = 6 \\\\times \\\\frac{1}{120} \\\\times (6 \\\\times 24) = 6 \\\\times \\\\frac{1}{120} \\\\times 48 = \\\\frac{288}{120} = 2.4\\\\ hours</p>\\n\\n<p>2. Next, we calculate the remaining work after the first 2 days:</p>\\n<p>Remaining work = 120 - 2.4 = 117.6\\\\ hours</p>\\n\\n<p>3. After the first 2 days, 4 more villagers join, making a total of 10 villagers. Therefore, the work done by 10 villagers per hour is:</p>\\n<p>Work done by 10 villagers = 10 \\\\times \\\\frac{1}{120} = \\\\frac{10}{120} = \\\\frac{1}{12}\\\\ hours.</p>\\n\\n<p>4. Now we calculate the time needed to complete the remaining work with 10 villagers:</p>\\n<p>Time to complete remaining work = \\\\frac{117.6}{\\\\frac{1}{12}} = 117.6 \\\\times 12 = 1411.2\\\\ hours</p>\\n\\n<p>5. Finally, we convert this time from hours into days:</p>\\n<p>Total days needed = \\\\frac{1411.2}{24} \\\\approx 58.80 days.</p>\\n\\n<p>Thus, it will take approximately 58.80 days for the villagers to complete the fountain.</p>"}	\N
MCQ-Single	<Pure Contextual> - <Word Problems> - <Setting up proper steps(questions that require users to properly setting up the steps to solve the questions)> - <Work and Time> - <Taxation> - <difficulty_level: 1>	612	3	2	Work Efficiency of Bakers in a Busy Day	In a quaint little town, a local bakery employs two bakers, Alice and Bob, who together have the ability to produce a batch of delicious pastries in 6 hours. However, Alice is known to be slightly faster; she can complete the same batch alone in 4 hours, while Bob, on the other hand, takes 12 hours. Given this context, if both bakers decide to work together on a busy Saturday, and they manage to produce an extra 3 batches within the duration of a single Saturday, how long did they take to make these extra batches during their busy working period?	1	0	0	{}	2025-02-07 06:47:24.511	2025-02-07 06:47:24.511	f	\N	\N	f	{"solution": "First, we calculate the work rates of Alice and Bob:<br>- Alice's work rate: ~~\\\\frac{1 \\\\text{ batch}}{4 \\\\text{ hours}} = 0.25 \\\\text{ batches per hour}~~<br>- Bob's work rate: ~~\\\\frac{1 \\\\text{ batch}}{12 \\\\text{ hours}} = 0.0833 \\\\text{ batches per hour}~~<br><br>Now, to find their combined work rate:<br>Combined work rate = ~~0.25 + 0.0833 = 0.3333 \\\\text{ batches per hour}~~<br><br>Next, we need to calculate the time taken to produce 3 batches:<br>Let \\\\( t \\\\) be the time in hours to produce 3 batches.<br>Thus, we have:<br><br>~~t \\\\times 0.3333 = 3~~<br><br>Solving for \\\\( t \\\\):<br>~~t = \\\\frac{3}{0.3333} \\\\approx 9 \\\\text{ hours}~~<br><br>Therefore, Alice and Bob took approximately 9 hours to make the extra 3 batches on that busy Saturday."}	\N
MCQ-Single	<Real Contextual> - <Arithmetic> - <common pitfalls> - <Percentages> - <difficulty_level: 3>	613	3	2	Calculating the Total Cost of Balloons with Discounts and Taxes	In a vibrant city fair, a booth sells colorful balloons at a fixed price. During the fair, the vendor decides to offer a promotional discount of 25% on all balloon purchases. If a shopper buys a total of 10 balloons, the original price per balloon is \\$4. After the discount, the shopper also encounters an unexpected 10% sales tax on the final price. What is the total amount the shopper spends on these 10 balloons after applying the discount and adding the sales tax? Be careful with the calculations, as rounding at different stages may lead to different outcomes.	3	0	0	{}	2025-02-07 06:47:24.54	2025-02-07 06:47:24.54	f	\N	\N	f	{"solution": "<html><p>To determine the total amount spent by the shopper on the balloons, we will follow these steps:</p><ol><li>Calculate the total original price of the balloons:</li> <p>\\\\( \\\\text{Total Original Price} = \\\\text{Price per Balloon} \\\\times \\\\text{Number of Balloons} = 4.00 \\\\times 10 = 40.00 \\\\, \\\\text{USD} \\\\)</p> <li>Calculate the discount amount:</li> <p>\\\\( \\\\text{Discount Amount} = \\\\text{Total Original Price} \\\\times \\\\text{Discount Percentage} = 40.00 \\\\times 0.25 = 10.00 \\\\, \\\\text{USD} \\\\)</p> <li>Calculate the price after discount:</li> <p>\\\\( \\\\text{Price After Discount} = \\\\text{Total Original Price} - \\\\text{Discount Amount} = 40.00 - 10.00 = 30.00 \\\\, \\\\text{USD} \\\\)</p> <li>Calculate the sales tax amount:</li> <p>\\\\( \\\\text{Sales Tax Amount} = \\\\text{Price After Discount} \\\\times \\\\text{Sales Tax Percentage} = 30.00 \\\\times 0.10 = 3.00 \\\\, \\\\text{USD} \\\\)</p> <li>Calculate the final price after tax:</li> <p>\\\\( \\\\text{Final Price} = \\\\text{Price After Discount} + \\\\text{Sales Tax Amount} = 30.00 + 3.00 = 33.00 \\\\, \\\\text{USD} \\\\)</p></ol><p>Thus, the total amount spent by the shopper on the balloons after applying the discount and adding the sales tax is \\\\$33.00.</p></html>"}	\N
MCQ-Single	<Pure Contextual> - <Algebra> - <Backsolving> - <Functions> - <difficulty_level: 1>	614	3	2	Finding the Total Cost of Lattes at a Quirky Café	A quirky café is known for serving unique flavored lattes. The café offers three sizes of lattes - small, medium, and large. If the price of a small latte is represented by \\( x \\), the medium latte costs \\( 1.5x \\), and the large latte costs \\( 2.2x \\). If a customer orders one small, one medium, and one large latte, what is the total cost in terms of \\( x \\)?	1	0	0	{}	2025-02-07 06:47:24.559	2025-02-07 06:47:24.559	f	\N	\N	f	{"solution": "To find the total cost of the lattes in terms of \\\\( x \\\\), we can calculate as follows:<br><br>1. The cost of a small latte is \\\\( x \\\\).<br>2. The cost of a medium latte is \\\\( 1.5x \\\\).<br>3. The cost of a large latte is \\\\( 2.2x \\\\).<br><br>Now, the total cost can be expressed as:<br>\\\\[ \\\\text{Total Cost} = x + 1.5x + 2.2x \\\\]<br>\\\\[ \\\\text{Total Cost} = (1 + 1.5 + 2.2)x \\\\]<br>\\\\[ \\\\text{Total Cost} = 4.7x \\\\]<br><br>Thus, the total cost of one small, one medium, and one large latte is \\\\( 4.7x \\\\)."}	\N
MCQ-Single	<Real Contextual> - <Word Problems> - <Setting up proper steps(questions that require users to properly setting up the steps to solve the questions)> - <Inequalities> - <Accounting> - <difficulty_level: 1>	615	3	2	Inequalities in Profit Management: An Accounting Dilemma	In a small accounting firm, Sarah is tasked with managing the financial records for two different clients, Client A and Client B. Client A's records are expected to generate a profit of at least \\$1,500, while Client B's records should yield a profit of at least \\$1,200. If Sarah's total profit from both clients cannot exceed \\$3,000 due to budget constraints set by her firm, which of the following inequalities represents the situation described? Let x represent the profit from Client A and y represent the profit from Client B.	1	0	0	{}	2025-02-07 06:47:24.588	2025-02-07 06:47:24.588	f	\N	\N	f	{"solution": "The situation can be represented by the following inequalities:<ul><li>\\\\( x \\\\geq 1500 \\\\) - Profit from Client A</li><li>\\\\( y \\\\geq 1200 \\\\) - Profit from Client B</li><li>\\\\( x + y \\\\leq 3000 \\\\) - Total profit constraint</li></ul>These inequalities reflect the requirements of profit generation set for Sarah in the accounting firm."}	\N
MCQ-Single	<Real Contextual> - <Word Problems> - <Mathematical tools(Questions which may have 2 or more mathematical approachs to solve, but user would have to choose the most optimal and efficient approach: generate question content in that manner)> - <Polynomials> - <Strategy and Management> - <difficulty_level: 4>	616	3	2	Optimizing Resource Allocation for Project Efficiency in Strategic Management	In a recent evaluation of a strategic management initiative aimed at enhancing project efficiency, a company's project manager devised a polynomial model representing the relationship between the number of resources allocated (x) and the completion time (y) in days for a specific project. The polynomial is defined as y = 3x^2 - 12x + 18, where x must be a positive integer. The management wants to assess the completion time as resources are adjusted, noting that they aim for a completion time no greater than 30 days. Considering the constraints involved in resource allocation, the project manager sets aside a budget allowing for the deployment of up to 8 resources. However, they also receive feedback from team members suggesting that employing a reduction strategy by redistributing existing resources could optimize completion time without exceeding the set budget. Based on this, what is the maximum number of resources that can be allocated while still ensuring the project is completed in accordance with the stipulated timeframe of 30 days?	4	0	0	{}	2025-02-07 06:47:24.618	2025-02-07 06:47:24.618	f	\N	\N	f	{"solution": "<p>To solve the problem, we start by setting the polynomial equal to 30, since we want to find when the project can be completed in at most 30 days:</p> <p>~~y = 3x^{2} - 12x + 18 = 30~~</p> <p>Rearranging gives:</p> <p>~~3x^{2} - 12x + 18 - 30 = 0~~</p> <p>Which simplifies to:</p> <p>~~3x^{2} - 12x - 12 = 0~~</p> <p>Now, we can factor or use the quadratic formula:</p> <p>Using the quadratic formula: ~~x = \\\\frac{-b \\\\pm \\\\sqrt{b^{2} - 4ac}}{2a}~~</p> <p>Where:\\n - a = 3\\n - b = -12\\n - c = -12</p> <p>Calculating the discriminant:</p> <p>~~b^{2} - 4ac = (-12)^{2} - 4(3)(-12) = 144 + 144 = 288~~</p> <p>Now applying the quadratic formula:</p> <p>~~x = \\\\frac{12 \\\\pm \\\\sqrt{288}}{6}~~</p> <p>This gives two possible solutions. However, since we are interested in positive integer values of x, we only consider those solutions which are greater than zero. Solving further:</p> <p>After calculating, the relevant solution for x that aligns with the conditions of resource allocation is approximately: ~~x \\\\approx 4.83~~</p> <p>Since x must be a positive integer, we take the maximum possible integer value, thus:</p> <p>The maximum number of resources that can be allocated while ensuring project completion within 30 days is: <strong>5</strong>.</p>"}	\N
MCQ-Single	<Pure Contextual> - <Algebra> - <Number Picking(by logical and critical reasoning over constraints given in the question)> - <Polynomials> - <difficulty_level: 5>	617	3	2	Polynomial Evaluation in a Competitive Scenario	In a mathematical competition, participants were tasked with solving a complex polynomial equation defined as -5x^2 + -8x + 5y + -2. The evaluators noticed that the first variable, x, is greatly affected by the value of y. To streamline the grading, it was determined that when x is set to 5, the total value of the polynomial must yield a sum close to -40. Only the candidates who can critically evaluate the function and correctly deduce the other values will pass. Which of the following values of y would allow the polynomial to satisfy the condition stated by the evaluators?	5	0	0	{}	2025-02-07 06:47:24.647	2025-02-07 06:47:24.647	f	\N	\N	f	{"solution": "<p>To determine the value of y that satisfies the polynomial equation, we start with the given values:</p> <p>Let \\\\( x = 5 \\\\) and we want the polynomial to sum up to \\\\( -40 \\\\).</p> <p>Substituting \\\\( x \\\\) into the polynomial:</p> <p>\\\\( -5x^{2} + -8x + 5y + -2 = -40 \\\\)</p> <p>This simplifies to:</p> <p>\\\\( -5(5)^{2} + -8(5) + 5y + -2 = -40 \\\\)</p> <p>Calculating the left-hand side:</p> <p>\\\\( -5(25) + -40 + 5y - 2 = -40 \\\\)</p> <p>Which simplifies to:</p> <p>\\\\( -125 + 5y - 2 = -40 \\\\)</p> <p>Now, combining the constants:</p> <p>\\\\( 5y - 127 = -40 \\\\)</p> <p>Adding 127 to both sides gives:</p> <p>\\\\( 5y = 87 \\\\)</p> <p>Dividing both sides by 5 yields:</p> <p>\\\\( y = \\\\frac{87}{5} = 17.4 \\\\)</p><p>Thus, the value of y that would allow the polynomial to satisfy the evaluators' condition is:</p> <p>\\\\( y = 17.4 \\\\)</p>"}	\N
MCQ-Single	<Real Contextual> - <Arithmetic> - <Critical Reasoning> - <Unitary Method> - <difficulty_level: 1>	618	3	2	Flour Calculation for Bread Production in a Bakery	In a small bakery, the baker uses 2 kg of flour to make 16 loaves of bread. If she wants to make 48 loaves, how much flour does she need to use? A helpful tip: think about how much flour is used for each loaf and then scale it accordingly.	1	0	0	{}	2025-02-07 06:47:24.674	2025-02-07 06:47:24.674	f	\N	\N	f	{"solution": "To determine the amount of flour required for 48 loaves, we first find out how much flour is used for one loaf.<br><br>1. Calculate flour per loaf:<br>   \\\\text{Flour per loaf} = \\\\frac{2 \\\\text{ kg}}{16 \\\\text{ loaves}} = 0.125 \\\\text{ kg per loaf}<br><br>2. Now, to find the flour needed for 48 loaves:<br>   \\\\text{Total flour for 48 loaves} = 0.125 \\\\text{ kg/loaf} \\\\times 48 \\\\text{ loaves} = 6.0 \\\\text{ kg}<br><br>Thus, the total amount of flour required to produce 48 loaves of bread is 6.0 kg."}	\N
MCQ-Single	<Pure Contextual> - <Algebra> - <Number Picking(by logical and critical reasoning over constraints given in the question)> - <Polynomials> - <difficulty_level: 2>	619	3	2	Maximizing Flowers Planted in a Community Garden Using a Polynomial Model	A local gardening club has decided to plant a new type of flower in their community garden. They have created a polynomial equation to model the number of flowers (f) they can plant based on the number of garden beds (b). The equation is given by f(b) = -1b^3 + 4b^2 + 1b + -4. The club currently has 4 garden beds available for planting. If they want to maximize the number of flowers planted while still staying within the positive integer quantity of flowers, what is the maximum number of flowers they can plant using their polynomial equation? Choose the appropriate number of garden beds they should use from the options provided.	2	0	0	{}	2025-02-07 06:47:24.706	2025-02-07 06:47:24.706	f	\N	\N	f	{"solution": "<h3>Solution:</h3> <p>To find the maximum number of flowers that can be planted using the polynomial equation <strong>f(b) = -1b^3 + 4b^2 + 1b - 4</strong>, we evaluate this polynomial for the integer values of garden beds (b) from 1 to 4:</p> <ul> <li>For b = 1: f(1) = -1(1^3) + 4(1^2) + 1(1) - 4 = 0</li> <li>For b = 2: f(2) = -1(2^3) + 4(2^2) + 1(2) - 4 = 6</li> <li>For b = 3: f(3) = -1(3^3) + 4(3^2) + 1(3) - 4 = 8</li> <li>For b = 4: f(4) = -1(4^3) + 4(4^2) + 1(4) - 4 = 0</li> </ul> <p>Thus, the maximum number of flowers that can be planted using 3 garden beds is <strong>8</strong>.</p>"}	\N
MCQ-Single	<Real Contextual> - <Word Problems> - <Assessing given Situation(checking the ability of accessing a given situation)> - <Polynomials> - <Taxation> - <difficulty_level: 1>	620	3	2	Calculating Tax Liability for a Small Business Based on Employee Count	In a bustling city, a government official proposed a new tax policy affecting the city's residents. The tax on small businesses is represented by the polynomial expression \\( P(x) = 2x^{2} + 3x + 5 \\), where \\( x \\) represents the number of employees in a small business. If a business has 3 employees, how much tax would the business owe? Calculate the tax using the polynomial provided and determine the total tax liability for a small business with 3 employees.	1	0	0	{}	2025-02-07 06:47:24.736	2025-02-07 06:47:24.736	f	\N	\N	f	{"solution": "To find the tax owed by a business with 3 employees, we will use the polynomial \\\\( P(x) = 2x^{2} + 3x + 5 \\\\). We will evaluate this polynomial at \\\\( x = 3 \\\\):<br><br>1. Substitute \\\\( x \\\\) into the polynomial:<br>   \\\\( P(3) = 2(3)^{2} + 3(3) + 5 \\\\)<br>2. Calculate \\\\( (3)^{2} = 9 \\\\):<br>   \\\\( P(3) = 2(9) + 3(3) + 5 \\\\)<br>3. Multiply: \\\\( 2(9) = 18 \\\\)<br>   \\\\( P(3) = 18 + 3(3) + 5 \\\\)<br>4. Calculate \\\\( 3(3) = 9 \\\\):<br>   \\\\( P(3) = 18 + 9 + 5 \\\\)<br>5. Add all terms: \\\\( P(3) = 18 + 9 + 5 = 32 \\\\)<br><br>Thus, the total tax liability for a small business with 3 employees is \\\\$ 32."}	\N
MCQ-Single	<Pure Contextual> - <Word Problems> - <Mathematical tools(Questions which may have 2 or more mathematical approachs to solve, but user would have to choose the most optimal and efficient approach: generate question content in that manner)> - <Percentages> - <Economics> - <difficulty_level: 4>	621	3	2	Optimal Price Setting in the Quirky Market Town Bakery	In a peculiar market town renowned for its extravagant economic festivals, a baker operates a quaint bakery. Last month, the baker decided to introduce a new line of prestige pastries priced at \\$4 each, hoping to increase his market share. He sold 150 pastries. Due to a pricing error, the baker also inadvertently marked down his classic cookies, which are normally priced at \\$2 each, by 25\\% to attract more customers. This resulted in the sale of 300 cookies in the same time frame. After observing that customers preferred cookies over pastries, the baker raised the prices of both items for the upcoming month. The new prices for pastries and cookies were set to be calculated based on the sales data from last month. If the market's demand fluctuated by a further 40\\% increase in cookie sales and a proportional decrease in pastry sales next month, what will be the best way to ascertain the optimal new prices to maintain profitability while ensuring that demand continues to grow? Consider how to best calculate the effects of price changes on the total revenue of both product lines before re-evaluating the price adjustments for the next month, taking into account both the price elasticity of demand and the new sales forecasts.	4	0	0	{}	2025-02-07 06:47:24.764	2025-02-07 06:47:24.764	f	\N	\N	f	{"solution": "<p>To find the optimal new prices for maintaining profitability while ensuring sales growth, we can break down the calculations as follows:</p><ol><li><p>The discounted price of cookies was calculated based on a 25% markdown:</p> <p>Cookie Price (Discounted) = \\\\$2 \\\\times (1 - 0.25) = \\\\$1.50</p></li><li><p>The total revenue generated from both pastries and cookies in the initial month was:</p> <p>Total Revenue (Initial) = (\\\\$4 \\\\times 150) + (\\\\$1.50 \\\\times 300) = \\\\$1050</p></li><li><p>With a projected 40% increase in cookie sales, the new forecast for cookie sales becomes:</p> <p>Cookie Sales (Forecasted) = 300 \\\\times (1 + 0.40) = 420</p></li><li><p>Conversely, the expected change in pastry sales, given a proportional decrease, can be anticipated as:</p> <p>Pastry Sales (Forecasted) = 150 \\\\times (1 - 0.40) = 90</p></li><li><p>Finally, estimating the total revenue for the following month with these projections keeping cookie prices at their standard current level:</p><p>Total Revenue (Forecasted) = (\\\\$4 \\\\times 90) + (\\\\$2 \\\\times 420) = \\\\$1200</p></li></ol><p>By assessment and retaining a firm grasp on both price elasticity and shifting market demands, the baker may now explore adjustments to optimize his prices after considering these revenue projections.</p>"}	\N
MCQ-Single	<Real Contextual> - <Word Problems> - <Mathematical tools(Questions which may have 2 or more mathematical approachs to solve, but user would have to choose the most optimal and efficient approach: generate question content in that manner)> - <Algebraic Equations> - <Resource Management> - <difficulty_level: 1>	622	3	2	Optimal Fishing Strategies: Balancing Demand and Sustainability on the Island	In a small island community, the local fishery has a sustainable fishing limit of 600 pounds per week. Due to an increase in demand, the fishery has decided to reassess its weekly fishing practices. The fishery currently operates $5.00 for every pound of fish caught and has fixed costs amounting to $300. The fishery's owner estimates that reducing fishing days from 6 to 4 would decrease the maximum capacity of fish caught significantly. Determine how many pounds of fish can be caught per day if they decide to fish only on 4 days this week while not exceeding the sustainable limit.	1	0	0	{}	2025-02-07 06:47:24.797	2025-02-07 06:47:24.797	f	\N	\N	f	{"solution": "To determine how many pounds of fish can be caught per day when fishing only on 4 days, we divide the total sustainable limit by the number of days fished. The calculation is as follows:<br><br>$$\\\\text{Pounds per day} = \\\\frac{\\\\text{Total Limit per Week}}{\\\\text{Fishing Days}} = \\\\frac{600 \\\\text{ pounds}}{4} = 150 \\\\text{ pounds per day}.$$<br><br>Thus, they can catch 150 pounds of fish per day."}	\N
MCQ-Single	<Pure Contextual> - <Algebra> - <Number Picking(by logical and critical reasoning over constraints given in the question)> - <Inequalities> - <difficulty_level: 2>	623	3	2	Velocity of a Comet: Determining Minimum Speed for Celestial Records	In a rare cosmic event, a particularly bright comet is traveling through our solar system. The velocity of the comet can be described by the inequality \\(v > 100 + 2x\\), where \\(v\\) is the velocity in kilometers per hour, and \\(x\\) is the number of days from its closest approach to Earth. If the comet passed by Earth 10 days ago, what is the minimum speed \\(v\\) at which the comet is traveling today, considering the influence of gravitational pull from neighboring celestial bodies that can alter its acceleration by up to 15 km/h? Express your answer in terms of \\(v\\) and determine the greatest possible rank that this comet could achieve in the top celestial speed records, keeping in mind that the velocity must exceed the average limit of 120 km/h required for such an accolade.	2	0	0	{}	2025-02-07 06:47:24.825	2025-02-07 06:47:24.825	f	\N	\N	f	{"solution": "<h2>Solution:</h2><p>Given the inequality for velocity \\\\(v > 100 + 2x\\\\), we first substitute \\\\(x = 10\\\\):</p><p>\\\\(v > 100 + 2(10) \\\\Rightarrow v > 100 + 20 \\\\Rightarrow v > 120\\\\)</p><p>Next, we need to factor in the influence from gravitational pull, which can add up to 15 km/h:</p><p>\\\\(v > 120 + 15 \\\\Rightarrow v > 135\\\\)</p><p>However, since we are looking for the greatest possible rank, we also need it to be above the average limit required for such accolade, which is 120 km/h. Thus:</p><p>\\\\(v = 135 \\\\text{ km/h} \\\\text{ (considering acceleration)}\\\\)</p><p>Therefore, the comet's speed must exceed \\\\(120 km/h\\\\) to achieve a record, confirmed by our findings:</p><p>Final minimum speed \\\\(v = 135 \\\\text{ km/h}\\\\</p>"}	\N
MCQ-Single	<Real Contextual> - <Arithmetic> - <Logical Reasoning> - <Trial and Error Method(type of questions)> - <difficulty_level: 2>	624	3	2	Calculation of Average Delivery Time in a Logistics Company	A logistics company is assessing its delivery system efficiency. They discovered that on Mondays, the average delivery time for packages is 8 hours. On Tuesdays, due to a temporary increase in workload, the average delivery time jumps to 10 hours. The company needs to calculate the average delivery time over the course of a week (Monday to Sunday). However, they realized that Wednesdays have a 20% reduction in delivery time compared to Mondays, while Thursdays have an increase of 15% compared to Tuesdays. Fridays are particularly busy, and their average delivery time is 12 hours, while Saturday deliveries are known to be quicker, averaging 7 hours. Finally, Sundays have a delivery time that is 25% longer than Saturdays. Given this information, what is the average delivery time across the entire week if the company is able to compute the total hours and divide by 7?	2	0	0	{}	2025-02-07 06:47:24.86	2025-02-07 06:47:24.86	f	\N	\N	f	{"solution": "To solve for the average delivery time over the week, we first calculate the individual delivery times:\\n<ul><li>Monday: 8 hours</li><li>Tuesday: 10 hours</li><li>Wednesday: 6.40 hours (20% reduction from Monday)</li><li>Thursday: 11.50 hours (15% increase from Tuesday)</li><li>Friday: 12 hours</li><li>Saturday: 7 hours</li><li>Sunday: 8.75 hours (25% longer than Saturday)</li></ul>Next, we find the total delivery time for the week:\\nTotal Delivery Time = 8 + 10 + 6.40 + 11.50 + 12 + 7 + 8.75\\nTotal Delivery Time = 63.65 hours\\n\\nFinally, to find the average delivery time:\\nAverage Delivery Time = \\\\frac{\\\\text{Total Delivery Time}}{7} = \\\\frac{63.65}{7} \\\\approx 9.09 \\\\text{ hours}."}	\N
MCQ-Single	<Pure Contextual> - <Word Problems> - <Setting up proper steps(questions that require users to properly setting up the steps to solve the questions)> - <Functions> - <Strategy and Management> - <difficulty_level: 1>	625	3	2	Calculating the Consulting Fee for a Startup Project	A small startup company specializes in providing strategic management consulting for various businesses. The consulting fee they charge is structured based on the functions involved in the project, specifically on the number of hours dedicated to the client's needs. For a particular project, they charge \\$100 per hour for the first 10 hours, and for any hours beyond that, they offer a 10\\% discount on the hourly rate. If a client requires 15 hours of consulting, what will be the total fee for the project?	1	0	0	{}	2025-02-07 06:47:24.889	2025-02-07 06:47:24.889	f	\N	\N	f	{"solution": "<html><p>To calculate the total consulting fee for the client, we will follow these steps:</p><ol><li>Calculate the fee for the first 10 hours:</li><p>\\\\( \\\\text{Fee for first 10 hours} = \\\\$100 \\\\times 10 = \\\\$1000 \\\\)</p><li>Determine the number of additional hours needed:</li><p>\\\\( \\\\text{Additional hours} = 15 - 10 = 5 \\\\text{ hours} \\\\)</p><li>Calculate the discounted hourly rate for additional hours:</li><p>\\\\( \\\\text{Discounted rate} = \\\\$100 \\\\times (1 - 0.10) = \\\\$90 \\\\)</p><li>Calculate the fee for the additional hours:</li><p>\\\\( \\\\text{Fee for additional hours} = \\\\$90 \\\\times 5 = \\\\$450 \\\\)</p><li>Finally, sum both fees to find the total:</li><p>\\\\( \\\\text{Total fee} = \\\\$1000 + \\\\$450 = \\\\$1450 \\\\)</p></ol></html>"}	\N
MCQ-Single	<Pure Contextual> - <Algebra> - <Backsolving> - <Inequalities> - <difficulty_level: 1>	626	3	2	Weight Combinations of Fruits in a Market Basket	In a quaint village, there are three types of fruits being sold at a local market. Apples are sold at \\$2 per kilogram, oranges at \\$3 per kilogram, and bananas at \\$1 per kilogram. A fruit vendor determines to mix these fruits and put together a fruit basket weighing a total of 10 kilograms. If the vendor wants to ensure that the weight of bananas is at least 2 kilograms but not more than 4 kilograms, how many kilograms of apples and oranges combined does the vendor need to include in the basket, provided that the weight of apples must be twice that of oranges? What are the possible weight combinations for apples and oranges under these constraints?	1	0	0	{}	2025-02-07 06:47:24.917	2025-02-07 06:47:24.917	f	\N	\N	f	{"solution": "<p>To solve the problem, we start by expressing the weight of apples and oranges using the given relationships:</p> <p>Let:</p> <ul> <li>Weight of apples = a</li> <li>Weight of oranges = o</li> <li>Weight of bananas = b</li> </ul> <p>According to the problem:</p> <ul> <li>The relationship between apples and oranges is: \\\\( a = 2o \\\\)</li> <li>And the total weight equation is: \\\\( a + o + b = 10 \\\\)</li> </ul> <p>Substituting the expression for apples into the total weight equation gives:</p> <p>\\\\( 2o + o + b = 10 \\\\)</p> <p>This simplifies to:</p> <p>\\\\( 3o + b = 10 \\\\)</p> <p>From this, we can express the weight of bananas as:</p> <p>\\\\( b = 10 - 3o \\\\)</p> <p>Next, we have the constraints for the weight of bananas:</p> <ul> <li>Minimum weight of bananas: \\\\( b \\\\geq 2 \\\\)</li> <li>Maximum weight of bananas: \\\\( b \\\\leq 4 \\\\)</li> </ul> <p>Setting these inequalities we find:</p> <p>For minimum weight:</p> <p>\\\\( 10 - 3o \\\\geq 2 \\\\Rightarrow 3o \\\\leq 8 \\\\Rightarrow o \\\\leq \\\\frac{8}{3} \\\\approx 2.67 \\\\)</p> <p>For maximum weight:</p> <p>\\\\( 10 - 3o \\\\leq 4 \\\\Rightarrow 3o \\\\geq 6 \\\\Rightarrow o \\\\geq 2 \\\\)</p> <p>Thus, the possible values of weight of oranges satisfying the conditions are approximately:</p> <ul> <li>2 kg</li> <li>2.33 kg</li> <li>2.67 kg</li> </ul> <p>Therefore, the combined weight of apples and oranges must be represented within these conditions.</p>"}	\N
MCQ-Single	<Real Contextual> - <Arithmetic> - <Critical Reasoning> - <Ratio and Proportion> - <difficulty_level: 1>	627	3	2	Finding the Number of Chocolate Muffins in a Bakery Based on Ratios	In a local bakery, the ratio of chocolate muffins to blueberry muffins is 4:3. If there are a total of 70 muffins in the bakery, how many chocolate muffins are there? To solve the problem, you must find the total parts represented by the ratio and then determine the portion that corresponds to chocolate muffins.	1	0	0	{}	2025-02-07 06:47:24.945	2025-02-07 06:47:24.945	f	\N	\N	f	{"solution": "To find the number of chocolate muffins, follow these steps:<br>1. The ratio of chocolate muffins to blueberry muffins is given as 4:3.<br>2. First, calculate the total parts in the ratio: \\\\(4 + 3 = 7\\\\).<br>3. To find the number of chocolate muffins, use the ratio: \\\\(\\\\frac{4}{7} \\\\times 70 = 40\\\\).<br>Thus, the total number of chocolate muffins is \\\\(40\\\\)."}	\N
MCQ-Single	<Pure Contextual> - <Arithmetic> - <Logical Reasoning> - <Unitary Method> - <difficulty_level: 2>	628	3	2	Earnings Comparison of Two Farmers at the Strawberry Festival	In a peculiar town known for its annual strawberry festival, the local farmers decided to distribute their strawberries in unique ways to attract more visitors. Farmer A sells his strawberries at a price of \\$3 per kilogram, while Farmer B sells his strawberries at \\$4 per kilogram. This year, Farmer A managed to sell 36 kilograms, which resulted in total proceeds of \\$108. Meanwhile, Farmer B reported an interesting outcome this season; for every kilogram sold, he noticed that if he sold twice as many kilograms as Farmer A, his earnings would total \\$X. If Farmer B sold 25 kilograms of strawberries this season, how much did he earn in total, and was he correct in his assumption? Calculate the total earnings and provide an explanation for the values used in your calculations.	2	0	0	{}	2025-02-07 06:47:24.974	2025-02-07 06:47:24.974	f	\N	\N	f	{"solution": "<p>Farmer A sold his strawberries at a price of \\\\$3 per kilogram. He sold 36 kilograms. The total earnings for Farmer A can be calculated as:</p>\\n\\n<p>\\\\(\\\\text{Total Earnings of Farmer A} = \\\\text{Price} \\\\times \\\\text{Kilograms Sold} = 3 \\\\times 36 = \\\\$108\\\\)</p>\\n\\n<p>Farmer B sells his strawberries at \\\\$4 per kilogram. He sold 25 kilograms. The total earnings for Farmer B can be calculated as:</p>\\n\\n<p>\\\\(\\\\text{Total Earnings of Farmer B} = \\\\text{Price} \\\\times \\\\text{Kilograms Sold} = 4 \\\\times 25 = \\\\$100\\\\)</p>\\n\\n<p>Thus, Farmer A earned \\\\$108 while Farmer B earned \\\\$100.</p>"}	\N
MCQ-Single	<Pure Contextual> - <Algebra> - <Backsolving> - <Algebraic Equations> - <difficulty_level: 5>	629	3	2	Finding the Number of Students and Schools in a Town Based on Given Equations	In a certain town, the population is represented by the equation 2x + 3y = 79 and the number of schools is given by y = \\frac{b}{x} + 5, where x represents the number of students and y represents the number of schools. If it is known that the number of students exceeds 40 by at least 7, which of the following values of x would satisfy both equations under the restriction that y must be an integer?	5	0	0	{}	2025-02-07 06:47:25.001	2025-02-07 06:47:25.001	f	\N	\N	f	{"solution": "To solve for the number of students (x) and schools (y), we start with the two equations given:<br> <br> 1. \\\\( 2x + 3y = 79 \\\\) <br> 2. \\\\( y = \\\\frac{8}{x} + 5 \\\\)<br> <br> Substituting the second equation into the first gives us:<br> \\\\( 2x + 3\\\\left(\\\\frac{8}{x} + 5\\\\right) = 79 \\\\)<br> Simplifying this equation leads to:<br> \\\\( 2x + \\\\frac{24}{x} + 15 = 79 \\\\)<br> which further reduces to:<br> \\\\( 2x + \\\\frac{24}{x} = 64 \\\\)<br> Multiplying through by x to eliminate the fraction results in:<br> \\\\( 2x^{2} - 64x + 24 = 0 \\\\)<br> Solving this quadratic equation using the quadratic formula yields two potential values for x:<br> \\\\( x = 16 - 2\\\\sqrt{61} \\\\) and \\\\( x = 2\\\\sqrt{61} + 16 \\\\).<br> Since we are looking for the integer value where the number of students exceeds 47 by 7, we take the second potential value which results in approximately 31.62. Therefore, the valid choice for the number of students is around 31, ensuring y remains an integer."}	\N
MCQ-Single	<Real Contextual> - <Algebra> - <Backsolving> - <Inequalities> - <difficulty_level: 3>	630	3	2	Inequalities in Theatre Ticket Sales	In a local theatre, the management has decided to set up an event where tickets are sold in two categories: Category A, which costs \\$15 each, and Category B, which costs \\$25 each. The theatre has a maximum seating capacity of 200 and seeks to achieve at least \\$3,000 in total ticket sales. If the number of tickets sold for Category A is represented by x and the number of tickets sold for Category B is represented by y, which of the following inequalities correctly represents the situation described, taking into account the limits on the seating and the sales threshold?	3	0	0	{}	2025-02-07 06:47:25.031	2025-02-07 06:47:25.031	f	\N	\N	f	{"solution": "<p>To represent the data given in the problem, we start with two key inequalities:</p>\\n<ul>\\n<li>1. The total ticket revenue must be at least \\\\$3000:</li>\\n<p>\\\\(15x + 25y \\\\geq 3000\\\\)</p>\\n<li>2. The total number of tickets sold must not exceed the seating capacity of 200:</li>\\n<p>\\\\(x + y \\\\leq 200\\\\)</p>\\n</ul>\\n<p>Now, we can solve each inequality for y:</p>\\n<ul>\\n<li>From the first inequality:</li>\\n<p>\\\\(y \\\\geq 120 - \\\\frac{3}{5}x\\\\)</p>\\n<li>From the second inequality:</li>\\n<p>\\\\(y \\\\leq 200 - x\\\\)</p>\\n</ul>\\n<p>With these derived expressions of y, we can analyze the constraints on ticket sales and seating arrangements.</p>"}	\N
MCQ-Single	<Real Contextual> - <Arithmetic> - <Number Sense> - <Percentages> - <difficulty_level: 5>	631	3	2	Florist's Pricing Dilemma: Calculating Minimum Selling Price for Wedding Arrangements	In a region known for its rare and exquisite flowers, a boutique florist specializes in creating stunning floral arrangements for various occasions. One day, the florist received an order for a grand wedding event that requested 150 white roses, 200 red tulips, and 250 blue orchids. Each type of flower has a different price based on its rarity. The white roses are priced at $3 each, the red tulips at $2.5 each, and the blue orchids at $4 each. As the florist plans the arrangement, they also need to consider an extra budget of 15% for transportation costs and a 10% discount on the total price due to a special vendor relationship. If the florist wants to achieve a profit margin of at least 20% on the final price, what should be the minimum selling price that the florist should charge for the wedding arrangements? Take each step carefully to ensure all costs, discounts, and desired profits are accurately considered, and calculate the final amount the florist should charge, rounding to the nearest cent.	5	0	0	{}	2025-02-07 06:47:25.059	2025-02-07 06:47:25.059	f	\N	\N	f	{"solution": "Solution not available"}	\N
CR	<philosophy> - <CR> - <draw inference/conclusion> - <difficulty_level: 4>	632	4	2	Inferences on Utilitarianism's Impact on Ethical Decisions	Based on the philosophy of utilitarianism discussed in the passage, what can be inferred about its influence on modern ethical decision-making?	4	0	0	{"passages": ["In recent years, a new philosophy has emerged advocating for the significance of emotional intelligence over traditional cognitive intelligence. Proponents argue that understanding and managing emotions is fundamental not only in personal relationships but also in professional environments. They assert that leaders who possess high emotional intelligence are more effective in fostering teamwork and motivating their subordinates. Furthermore, studies indicate that teams led by emotionally intelligent leaders tend to outperform those led by leaders lacking in this skill. Critics, however, question whether emotional intelligence is truly more important than cognitive intelligence in decision-making processes. They cite instances where analytical skills and technical knowledge have led to significant breakthroughs in various fields. As the debate continues, many organizations are starting to prioritize emotional intelligence training alongside traditional cognitive skill development.", "The philosophy of utilitarianism posits that the best action is the one that maximizes utility, generally defined as that which produces the greatest well-being of the greatest number of people. This approach is often applied in ethical reasoning and policy-making. Proponents of utilitarianism argue that it provides a clear framework for evaluating the consequences of actions and choices. However, critics claim that utilitarianism can sometimes lead to morally questionable decisions if the overall utility justifies harming a minority. Despite these criticisms, recent studies in social behavior indicate that societies tend to favor utilitarian principles when making collective decisions, suggesting that such philosophies may strongly influence public policy and societal norms. As more leaders and policymakers embrace these principles, there is a growing question about the long-term implications of utilitarianism on ethical standards and individual rights."]}	2025-02-07 06:47:25.089	2025-02-07 06:47:25.089	f	\N	\N	f	{"solution": "The correct answer is B: <br> Utilitarian principles likely contribute to a more collective approach in ethical decision-making. The passage indicates that societies tend to favor utilitarian principles when making collective decisions, suggesting a significant influence on modern ethical reasoning. <o> <br> Option A is incorrect because the passage does not state that utilitarianism has been completely rejected; rather, it highlights an ongoing debate. <o> <br> Option C is incorrect, as the passage emphasizes that utilitarianism may lead to morally questionable decisions, but it does not imply that individual rights are prioritized. <o> <br> Option D is incorrect because the passage suggests that utilitarianism does influence public policy, indicating its relevance and effectiveness. <o> <br> Option E is also incorrect as it contradicts the evidence presented in the passage regarding the acceptance of utilitarian principles in social decision-making."}	\N
CR	<physical_sciences> - <CR> - <complete the argument> - <difficulty_level: 1>	633	4	2	Completing the Argument on Physical Activity Benefits in Schools	Which of the following, if true, would most logically complete the argument presented in the passage about the benefits of physical activity in schools?	1	0	0	{"passages": ["Recent advancements in solar energy technology have made it significantly more efficient and accessible. As a result, many households are not only adopting solar panels for their energy needs but are also selling excess energy back to the grid. This shift indicates a move toward a more sustainable and economically viable energy future. Therefore, if more households transition to solar energy technologies, the overall carbon footprint of residential energy consumption will be greatly reduced.", "In recent years, researchers have discovered that exercise has not only physical benefits but also significant mental health benefits. Studies show that regular physical activity can alleviate symptoms of anxiety and depression. This is particularly important as mental health issues continue to rise globally. Therefore, if schools incorporate more physical activity into their curriculums, students will likely experience improved mental health and overall well-being."]}	2025-02-07 06:47:25.107	2025-02-07 06:47:25.107	f	\N	\N	f	{"solution": "The correct answer is E. Research shows that students who engage in physical activity have lower stress levels, which directly supports the argument that incorporating physical activity into school curriculums will improve mental health and overall well-being.<br><o>Option A is incorrect because while it mentions barriers to participation, it does not strengthen the conclusion about the positive impacts of exercise on mental health.<br><o>Option B is incorrect because, although it discusses academic performance, it does not explicitly address mental health benefits.<br><o>Option C is incorrect as it introduces a negative aspect of physical activity but fails to complete the argument in a way that supports the conclusion.<br><o>Option D is also incorrect since it highlights student preferences for sedentary activities, which undermines the argument rather than completing it."}	\N
CR	<culture> - <CR> - <draw inference/conclusion> - <difficulty_level: 1>	634	4	2	Impact of Social Media on Youth Culture	Based on the passage, what can be concluded about the impact of social media on youth culture?	1	0	0	{"passages": ["In recent years, a significant rise in vegetarianism has been observed in urban populations across various countries. This increase is often attributed to heightened awareness of health issues, environmental concerns, and animal rights. In many cities, vegetarian restaurants are flourishing, and more grocery stores are stocking plant-based products than ever before. Surveys indicate that younger generations are particularly inclined towards adopting vegetarian diets, suggesting that this trend may lead to lasting changes in dietary habits. Given these observations, it can be inferred that urban culture is evolving to become more health-conscious and ethical.", "Recent studies have shown that social media platforms are profoundly influencing youth culture. Teenagers increasingly rely on these platforms for entertainment, information, and connection with peers. As a result, traditional forms of communication, such as face-to-face interactions and phone calls, have seen a decline. Furthermore, a survey revealed that 75% of teenagers prefer to share experiences online rather than in person. This evidence suggests that social media not only shapes their interests and opinions but also alters the way they build relationships, indicating a shift in cultural norms among younger generations."]}	2025-02-07 06:47:25.124	2025-02-07 06:47:25.124	f	\N	\N	f	{"solution": "The correct answer is B: Teenagers are increasingly sharing experiences online over traditional communication methods.<br> This statement accurately reflects the passage's conclusion that teenagers prefer to share their experiences on social media rather than through face-to-face interactions, indicating a shift in cultural norms.<br> <o>Option A is incorrect because the passage states that traditional forms of communication, such as face-to-face interactions, have declined due to social media use.<br> <o>Option C is incorrect as the passage does not mention any increased popularity of traditional media sources.<br> <o>Option D is incorrect because the passage clearly indicates that social media has a significant influence on how teenagers connect with one another.<br> <o>Option E is incorrect as the passage does not discuss teenagers' preferences for obtaining information from books over online sources."}	\N
CR	<social_sciences> - <CR> - <draw inference/conclusion> - <difficulty_level: 4>	635	4	2	Impacts of Public Libraries on Civic Engagement	Based on the findings of the study by the Institute for Urban Development, which of the following conclusions can be drawn regarding public libraries and civic engagement?	4	0	0	{"passages": ["Recent research shows that urban parks significantly enhance the quality of life for city residents. A study conducted in various metropolitan areas revealed that individuals living near parks reported higher levels of physical activity, improved mental health, and greater community engagement. Despite these positive outcomes, many urban parks are underfunded and suffer from neglect. Consequently, urban planners argue that investment in parks is crucial for fostering healthy communities. The data suggests that increased park funding could lead to better public health outcomes. However, some critics claim that the benefits of parks are overstated and that funds could be allocated to other pressing needs, such as housing or transportation infrastructure.", "A recent study by the Institute for Urban Development found that people who utilize public libraries are more likely to be involved in civic activities, such as volunteering and voting, than those who do not. The study surveyed several communities and noted that in areas with well-resourced libraries, residents engaged in democratic processes at significantly higher rates. Library advocates argue that this indicates a link between access to information and active civic participation. However, skeptics remind us that correlation does not imply causation, suggesting that those who frequent libraries might already be inclined towards civic involvement for other reasons. This leads to an ongoing debate about the true impact of public libraries on community engagement."]}	2025-02-07 06:47:25.14	2025-02-07 06:47:25.14	f	\N	\N	f	{"solution": "The correct answer is D: The findings support the idea that using libraries correlates with increased civic participation.<br> <o>This option is directly supported by the study's conclusion that users of public libraries engage more in civic activities compared to non-users.</o><br> <o>Option A is too strong, as it states libraries are essential, while the study only shows correlation, not causation.</o><br> <o>Option B introduces an unrelated variable—education—without evidence from the passage.</o><br> <o>Option C incorrectly states that access to libraries has no relationship with voting rates, contradicting the findings of increased civic activity.</o><br> <o>Option E is misleading as it suggests that only well-resourced libraries have an impact, while the passage does not isolate the effect of resource levels.</o>"}	\N
CR	<philosophy> - <CR> - <evaluate the conclusion> - <difficulty_level: 1>	636	4	2	Evaluating Conclusions on Moral Relativism in Ethical Debates	Based on the passage, which of the following conclusions can be accurately drawn regarding moral relativism and its implications for ethical debates?	1	0	0	{"passages": ["Philosophers often argue about the nature of truth and its relationship to reality. Some contend that truth is an objective characteristic, independent of human perception, while others believe that truth is subjective, shaped by cultural and individual contexts. A recent debate highlighted this divide, with proponents of objective truth arguing that scientific discoveries reveal universal truths about the world, while advocates for subjective truth claim that different perspectives can lead to equally valid interpretations of realities. Ultimately, the discussion poses critical questions about how we evaluate the conclusions we draw from our experiences and observations.", "In philosophy, the concept of moral relativism suggests that moral judgments are not absolute but rather shaped by cultural, societal, and personal influences. Proponents argue that what is considered right or wrong can vary from one society to another, and as such, no single moral framework should be viewed as superior. This position raises important considerations for ethical debates, as it challenges the validity of universal moral principles. Critics, however, argue that this view can lead to a dangerous tolerance of harmful practices, suggesting a need for some overarching moral standards. Thus, the ongoing discourse about moral relativism and its implications invites us to critically evaluate the conclusions drawn about ethics in a diverse world."]}	2025-02-07 06:47:25.157	2025-02-07 06:47:25.157	f	\N	\N	f	{"solution": "The correct answer is C: Critics of moral relativism argue for the necessity of universal moral standards to prevent harm.<br><o>This option accurately reflects the passage's discussion about how critics of moral relativism see the potential dangers of a lack of absolute ethical guidelines.</o><br><o>Option A is incorrect because it misrepresents moral relativism; while it recognizes different moral perspectives, it does not claim they are all equally valid without context.</o><br><o>Option B is also incorrect as it suggests that proponents of moral relativism advocate for a singular dominant perspective, which contradicts their fundamental belief in the multiplicity of moral views.</o><br><o>Option D is misleading since moral relativism recognizes that ethical practices may differ across cultures, implying that practices can evolve over time.</o><br><o>Lastly, option E is incorrect because the debate on moral relativism is highly relevant to contemporary ethical discussions, as evidenced by ongoing ethical dilemmas in diverse societies.</o>"}	\N
CR	<philosophy> - <CR> - <find the assumption> - <difficulty_level: 2>	637	4	2	Identify the assumption in deontological ethics regarding moral actions	What assumption is made by the proponent of deontological ethics in the argument presented regarding moral actions and their consequences?	2	0	0	{"passages": ["The philosophical notion of utilitarianism posits that the best action is one that maximizes utility, typically defined as that which produces the greatest well-being of the greatest number of people. Some critics argue that this approach fails to take into account the long-term consequences of actions, focusing instead on immediate outcomes. However, proponents claim that by prioritizing overall happiness, utilitarianism leads to more ethical decision-making. Therefore, they argue that when faced with a moral dilemma, one should always opt for the course of action that benefits the majority.", "In examining moral philosophies, one often encounters deontological ethics, which assert that the morality of an action is based on whether that action itself is fundamentally right or wrong, regardless of the consequences. This view is contrasted with consequentialist theories, which judge actions based on their outcomes. A common assumption underlying deontological perspectives is that there are inherent moral rights and duties that do not depend on the potential results of an action. Thus, when making ethical decisions, it is crucial to recognize these moral imperatives."]}	2025-02-07 06:47:25.173	2025-02-07 06:47:25.173	f	\N	\N	f	{"solution": "<o>The correct answer is B: 'There are actions that are inherently right or wrong regardless of outcomes.' This statement captures the core assumption of deontological ethics, which posits that moral actions are judged based on their own intrinsic nature rather than their consequences.</o><br><o>Option A is incorrect because it contradicts the foundational principle of deontology, which emphasizes that moral rights and duties exist independently of consequences.</o><br><o>Option C is incorrect as it references a consequentialist perspective rather than a deontological one, which does not prioritize outcomes in moral decision-making.</o><br><o>Option D is incorrect because it advocates for consequentialism, which deontological ethics explicitly stands against.</o><br><o>Option E is incorrect as it conflates deontological ethics with a perspective that prioritizes individual happiness over collective good, which is not a tenet of deontology.</o>"}	\N
CR	<culture> - <CR> - <paradox> - <difficulty_level: 1>	638	4	2	Understanding the Paradox of Cultural Identity and Transformation	What is the paradox presented in the passage concerning cultural identity and its transformation?	1	0	0	{"passages": ["In many societies, cultural practices are often seen as rigid and unchanging. However, historical evidence suggests that cultures are not static; they evolve over time in response to various factors such as globalization, technological advancements, and social movements. This presents a paradox: while many individuals may strongly identify with and cling to their cultural traditions, these very traditions may be changing or disappearing as society progresses. Hence, the question arises: how can a culture be both a source of identity and a subject to transformation?", "Cultural identity is often perceived as a fixed and uniform characteristic that individuals possess. Yet, the reality is often contradictory. On one hand, people take pride in their heritage and maintain traditions that have been passed down through generations. On the other hand, exposure to different cultures through travel, migration, or technology frequently leads individuals to adopt new practices and beliefs that may dilute their original cultural identities. This raises a paradox: how can one claim to uphold their cultural heritage while simultaneously embracing influences from other cultures?"]}	2025-02-07 06:47:25.19	2025-02-07 06:47:25.19	f	\N	\N	f	{"solution": "The correct answer is B: <br> Cultural practices evolve in response to external influences while still being embraced by individuals. This option reflects the paradox described in the passage, where individuals maintain a sense of cultural identity even as they adapt to new influences. <br> <o> Option A is incorrect because it ignores the dynamic nature of cultural identity that the passage discusses. <br> <o> Option C is incorrect as it suggests that outside influences must be completely rejected, contradicting the concept of cultural evolution presented in the passage. <br> <o> Option D is incorrect because the passage implies that cultural transformation has been ongoing throughout history, not just a recent phenomenon. <br> <o> Option E is also incorrect because it fails to recognize that cultural identity can, and often does, incorporate change and adapt over time."}	\N
CR	<history> - <CR> - <complete the argument> - <difficulty_level: 1>	639	4	2	Completion of the Argument on the Renaissance's Impact	Based on the passage, which of the following best completes the argument: 'Thus, the Renaissance not only revived classical knowledge but also ________.'	1	0	0	{"passages": ["The ancient Greeks made significant contributions to the fields of art, science, and philosophy, which have continued to influence modern civilization. For instance, their development of democratic principles laid the foundation for contemporary political systems. Furthermore, their innovative approaches in mathematics and geometry, such as the Pythagorean theorem, have shaped the way we understand the world today. Therefore, one can argue that without the contributions of the ancient Greeks, our understanding of democracy, art, and science would be markedly different.", "During the Renaissance period, a revival of interest in classical knowledge began to spread across Europe. This movement not only led to advancements in art and architecture but also spurred significant progress in science and technology. For example, Leonardo da Vinci's studies of anatomy improved our understanding of the human body, while Galileo's innovations in astronomy changed how we perceive our place in the universe. Therefore, it can be concluded that the Renaissance was a pivotal time that not only celebrated the achievements of ancient civilizations but also laid the groundwork for modern scientific inquiry."]}	2025-02-07 06:47:25.207	2025-02-07 06:47:25.207	f	\N	\N	f	{"solution": "The correct answer is A: 'initiated a new era of artistic expression and scientific exploration.' This option logically follows the passage's argument that the Renaissance built upon classical knowledge and contributed significantly to advancements in various fields.<br> <o>Option B is incorrect because the passage highlights significant progress in philosophical thought during the Renaissance.</o> <br> <o>Option C is incorrect as the passage clearly states the profound impact of the Renaissance on modern society.</o> <br> <o>Option D is inaccurate because the passage discusses broader achievements beyond just the revival of Greek art.</o> <br> <o>Option E is also incorrect since the passage emphasizes advancements in technology and science rather than restrictions.</o>"}	\N
CR	<history> - <CR> - <strengthen the argument> - <difficulty_level: 1>	640	4	2	Strengthening the Argument for the Printing Press's Role in the Renaissance	Which of the following, if true, would most strengthen the argument that the printing press was instrumental in shaping the transformative nature of the Renaissance?	1	0	0	{"passages": ["Throughout history, many civilizations have thrived primarily due to their innovations in agricultural practices. For instance, the ancient Mesopotamians developed irrigation systems that allowed them to control water flow, which in turn significantly boosted their crop yields. This advancement in agriculture helped sustain larger populations and facilitated trade. Consequently, it is clear that agricultural innovation is not merely a supportive element but a critical factor in the success and expansion of civilizations.", "The Renaissance, a period of significant cultural and intellectual revival in Europe, was largely fueled by the increased availability of printed materials. The invention of the printing press allowed for the rapid dissemination of ideas, particularly those related to science and philosophy. This surge in accessible knowledge not only inspired advancements in various fields but also empowered individuals to challenge traditional beliefs. Therefore, it can be posited that the printing press was instrumental in shaping the transformative nature of the Renaissance."]}	2025-02-07 06:47:25.223	2025-02-07 06:47:25.223	f	\N	\N	f	{"solution": "The correct answer is C. This statement directly supports the argument by indicating that classical texts, which were vital to the intellectual advancements of the Renaissance, became widely accessible because of the printing press. <br> <o> Option A, while true, only discusses the limitations of handwritten manuscripts without connecting it to the transformative nature of the Renaissance. <br> <o> Option B discusses a decline in religious influence but does not directly relate to how the printing press contributed to broader knowledge dissemination. <br> <o> Option D highlights economic prosperity but does not specifically address the role of the printing press. <br> <o> Option E contradicts the argument that the printing press was instrumental in shaping the Renaissance by suggesting it was only used for religious texts, thereby weakening the overall argument."}	\N
		641	4	2	Implications of Physical Sciences in Technological Advancements	What can be inferred about the practical significance of thermodynamics, quantum mechanics, and electromagnetism in modern technology based on the passages?	-1	0	0	{}	2025-02-07 06:47:25.245	2025-02-07 06:47:25.245	t	63	\N	f	{"solution": "<p>The correct answer is <strong>A</strong>: These scientific principles are essential for the development of innovative technologies, such as renewable energy and quantum computing.</p><p>This option accurately reflects the implications drawn from the passages, which discuss how thermodynamics, quantum mechanics, and electromagnetism are not only foundational theories but also crucial for advancing technology.</p><p><strong>B</strong>: The principles of physical sciences have no significant impact on contemporary technological applications. <em>This statement is incorrect as the passages highlight the direct applications of these scientific principles in various technologies.</em></p><p><strong>C</strong>: Understanding these concepts is primarily important for academic purposes and does not influence real-world technology. <em>The passages clearly indicate that these principles are vital for practical applications, thus this option is also incorrect.</em></p><p><strong>D</strong>: Scientific advances in physics are solely confined to theoretical frameworks and do not translate into practical applications. <em>This statement contradicts the essence of the passages, which emphasize the significant real-world applications of physical sciences.</em></p>"}	\N
		642	4	2	The Transformative Role of Quantum Mechanics in Understanding Reality	What can be inferred about the role of quantum mechanics in reshaping our understanding of reality based on the passages?	-1	0	0	{}	2025-02-07 06:47:25.264	2025-02-07 06:47:25.264	t	63	\N	f	{"solution": "<p>The correct answer is <strong>A</strong>: Quantum mechanics fundamentally alters our perception of reality by introducing concepts such as wave-particle duality and entanglement.</p><p>This option accurately reflects the implications of the passage, which discusses how quantum mechanics challenges classical intuitions and prompts a reconsideration of the nature of reality.</p><p><strong>B</strong>: The principles of quantum mechanics are confirmed by classical physics, providing no significant change in our understanding of reality. <em>This statement is incorrect as the passage highlights that quantum mechanics challenges and redefines, rather than confirms, classical physics.</em></p><p><strong>C</strong>: Quantum mechanics leads to practical benefits only, without affecting theoretical frameworks. <em>This is incorrect since the passage emphasizes that quantum mechanics not only has practical applications but also alters theoretical understandings of reality.</em></p><p><strong>D</strong>: The theories in quantum mechanics support the idea that reality operates solely on deterministic principles. <em>This statement is inaccurate; the passage illustrates that quantum mechanics introduces indeterminacy and complexities that contradict purely deterministic views.</em></p>"}	\N
		643	4	2	Consequences of Maxwell's Equations in Electromagnetism	According to the passage, what is a consequence of Maxwell's equations in relation to electricity and magnetism?	-1	0	0	{}	2025-02-07 06:47:25.282	2025-02-07 06:47:25.282	t	63	\N	f	{"solution": "<p>The correct answer is <strong>A</strong>: Maxwell's equations describe how electric charges create electric fields.</p><p>This statement is directly supported by the passage, which outlines that one of the key roles of Maxwell's equations is to explain the interaction between electric and magnetic fields.</p><p><strong>B</strong>: Maxwell's equations provide an argument that electricity and magnetism are completely independent phenomena. <em>This statement is incorrect as the passage illustrates that electricity and magnetism are interconnected through Maxwell's equations.</em></p><p><strong>C</strong>: Maxwell's equations emphasize that electric currents cannot generate magnetic fields. <em>This is inaccurate; the passage states that changing magnetic fields generate electric currents, contradicting this option.</em></p><p><strong>D</strong>: Maxwell's equations state that electric fields do not influence magnetic fields. <em>This statement is also incorrect since Maxwell's equations highlight the intricate relationship between electric and magnetic fields.</em></p>"}	\N
		644	4	2	Analyzing the Interconnectedness in Physical Sciences	What is the primary strength of the argument presented in the passage regarding the interconnectedness of various scientific principles in understanding physical phenomena?	-1	0	0	{}	2025-02-07 06:47:25.305	2025-02-07 06:47:25.305	t	64	\N	f	{"solution": "<p>The correct option is <strong>A</strong>: <em>The argument highlights how advancements in one scientific field can lead to breakthroughs in others, demonstrating their mutual reliance.</em> This reflects the passage's emphasis on the interdependencies among various scientific disciplines and how they collaborate to enhance our understanding of physical phenomena.</p> <p>Option <strong>B</strong> is incorrect because it contradicts the passage's assertion that different scientific fields are interconnected rather than independent.</p> <p>Option <strong>C</strong> is incorrect as the passage does not promote a singular approach to solving climate change, but rather highlights the need for an interdisciplinary method.</p> <p>Option <strong>D</strong> is also incorrect because the passage discusses the complexities and probabilistic nature of scientific laws, not a purely deterministic perspective.</p>"}	\N
		645	4	2	Inference on Interdisciplinary Research in Global Challenges	What can be inferred from the passage about the role of interdisciplinary research in addressing global challenges?	-1	0	0	{}	2025-02-07 06:47:25.322	2025-02-07 06:47:25.322	t	64	\N	f	{"solution": "<p>The correct option is <strong>B</strong>: <em>Collaborative efforts among various scientific fields enhance the effectiveness of solutions to complex problems like climate change.</em> This inference aligns with the passage's discussion on the necessity of interdisciplinary research to understand and address environmental issues.</p> <p>Option <strong>A</strong> is incorrect because it misrepresents the passage; it suggests that interdisciplinary research is less important, while the passage advocates for its importance.</p> <p>Option <strong>C</strong> is incorrect since the passage argues for the complexity of environmental issues, implying that single-discipline studies may not suffice.</p> <p>Option <strong>D</strong> is also incorrect as the passage focuses on the significance of collaboration in scientific research, rather than suggesting motivations related to funding opportunities.</p>"}	\N
		646	4	2	Detail on the Principle of Matter and Mass	According to the passage, what scientific principle is described as providing insight into why matter has mass?	-1	0	0	{}	2025-02-07 06:47:25.34	2025-02-07 06:47:25.34	t	64	\N	f	{"solution": "<p>The correct option is <strong>C</strong>: <em>Einstein's theory of relativity</em>. The passage explicitly states that this theory provides insight into why matter has mass, particularly through the context of the Higgs boson and the Higgs field.</p> <p>Option <strong>A</strong> is incorrect because, while the standard model of particle physics is mentioned, it does not specifically address why matter has mass.</p> <p>Option <strong>B</strong> is incorrect as the laws of thermodynamics are discussed in relation to energy transformations but not directly linked to the concept of mass.</p> <p>Option <strong>D</strong> is also incorrect as the principle of superposition pertains to quantum mechanics, which does not directly explain the mass of matter as described in the passage.</p>"}	\N
		647	4	2	Primary Purpose of the Passage on Physical Sciences	What is the primary purpose of the passage regarding the field of physical sciences?	-1	0	0	{}	2025-02-07 06:47:25.357	2025-02-07 06:47:25.357	t	64	\N	f	{"solution": "<p>The correct option is <strong>B</strong>: <em>To highlight the interconnectedness of various scientific principles and the importance of interdisciplinary research.</em> The passage emphasizes how different scientific fields are connected and discusses the necessity of collaboration to address complex issues like climate change.</p> <p>Option <strong>A</strong> is incorrect because the passage does not focus on historical developments but rather on current scientific understandings and their applications.</p> <p>Option <strong>C</strong> is incorrect as the passage does not delve into specific physical laws or their mathematical formulations, but rather discusses broad principles and concepts.</p> <p>Option <strong>D</strong> is also incorrect since the passage does not present physical sciences as subjective; it discusses the objective nature of scientific inquiry and collaboration.</p>"}	\N
		648	4	2	Organizational Structure of Historical Developments	What is the primary organizational structure used in the passage to discuss the major historical events such as the Renaissance, the Age of Exploration, and the Industrial Revolution?	-1	0	0	{}	2025-02-07 06:47:25.379	2025-02-07 06:47:25.379	t	65	\N	f	{"solution": "<p>The primary organizational structure used in the passage is:</p> <p><strong>A: Chronological order emphasizing the sequence of events.</strong> This option is correct because the passage discusses historical eras in the order they occurred (Renaissance, Age of Exploration, and Industrial Revolution), clearly illustrating their chronological development.</p> <p><strong>B: Comparative analysis linking different cultural effects.</strong> This option is incorrect as the passage does not primarily compare different cultural effects in a side-by-side format, but rather presents events in a sequential manner.</p> <p><strong>C: Thematic organization focusing on technological advancements.</strong> This option is not entirely accurate, since while technology is mentioned, the passage primarily focuses on distinct historical periods rather than categorizing them thematically based only on technological advancements.</p> <p><strong>D: Discrete sections highlighting individual historical figures.</strong> This option is incorrect because the passage discusses broader historical movements rather than isolating individual figures in separate sections.</p>"}	\N
		649	4	2	Inference on the Renaissance's Influence on Science	Based on the passage, what inference can be drawn about the impact of the Renaissance on future scientific developments?	-1	0	0	{}	2025-02-07 06:47:25.397	2025-02-07 06:47:25.397	t	65	\N	f	{"solution": "<p>The correct answer is:</p> <p><strong>C: The emphasis on humanism during the Renaissance encouraged scientific exploration.</strong> This option is correct because the passage describes the Renaissance as a period that emphasized humanism and a revival of learning, which inherently fostered an environment ripe for scientific inquiry and exploration.</p> <p><strong>A: The Renaissance stifled scientific innovation due to its focus on art.</strong> This option is incorrect as the passage suggests that the flourishing of arts and sciences occurred simultaneously, rather than one hindering the other.</p> <p><strong>B: Scientific advancements were divorced from the intellectual climate of the Renaissance.</strong> This option is incorrect because the passage implies that the intellectual climate of the Renaissance, characterized by humanism, was integral to the advances in various fields, including science.</p> <p><strong>D: The Renaissance had no significant impact on science according to the passage.</strong> This option is incorrect since the passage outlines how the Renaissance's cultural movements and emphasis on learning indeed laid the groundwork for future scientific developments.</p>"}	\N
		650	4	2	Technological Innovation of the Renaissance	Which technological innovation is credited to Johannes Gutenberg that had a significant impact during the Renaissance?	-1	0	0	{}	2025-02-07 06:47:25.415	2025-02-07 06:47:25.415	t	65	\N	f	{"solution": "<p>The correct answer is:</p> <p><strong>C: The printing press.</strong> This option is correct because the passage explicitly states that Johannes Gutenberg's invention of the printing press revolutionized the dissemination of knowledge during the Renaissance, allowing ideas to spread more widely and efficiently.</p> <p><strong>A: The steam engine.</strong> This option is incorrect as the steam engine is associated with the later stages of the Industrial Revolution, not the Renaissance.</p> <p><strong>B: The spinning jenny.</strong> This option is also incorrect because the spinning jenny was an invention that emerged much later during the Industrial Revolution, significantly impacting textile production rather than the Renaissance.</p> <p><strong>D: The mechanical clock.</strong> This option is incorrect since while clocks were important for timekeeping, the passage does not attribute their invention or significance to Gutenberg or the Renaissance period specifically.</p>"}	\N
		651	4	2	Primary Purpose of the Passage on Historical Transformations	What is the primary purpose of the passage regarding transformative historical eras?	-1	0	0	{}	2025-02-07 06:47:25.433	2025-02-07 06:47:25.433	t	65	\N	f	{"solution": "<p>The correct answer is:</p> <p><strong>B: To illustrate the interconnectedness of major historical events and their impacts on society.</strong> This option is correct because the passage discusses the Renaissance, Age of Exploration, and Industrial Revolution as transformative periods that influenced each other and shaped modern society through cultural and technological advancements.</p> <p><strong>A: To highlight the negative consequences of exploration and industrialization.</strong> This option is incorrect as the passage does not solely focus on the negative consequences; it emphasizes the broader influence of these eras on progress and human experience.</p> <p><strong>C: To provide a detailed timeline of important inventions in history.</strong> This option is incorrect because the passage is not structured as a timeline or list of inventions, rather it provides a thematic discussion of historical movements.</p> <p><strong>D: To argue against the notion that art influences scientific progress.</strong> This option is incorrect since the passage supports the idea that art and science flourished together during the Renaissance, rather than opposing it.</p>"}	\N
		652	4	2	Traits of Resilience in Psychology	According to the passage, which of the following traits is commonly associated with resilient individuals?	-1	0	0	{}	2025-02-07 06:47:25.455	2025-02-07 06:47:25.455	t	66	\N	f	{"solution": "<p>The correct answer is <strong>C: Optimism</strong>. The passage explicitly states that resilient individuals often possess traits such as optimism, highlighting its importance in adapting to adverse situations.</p> <p><strong>A: Cognitive inflexibility</strong> is incorrect. The passage discusses cognitive flexibility as a trait associated with resilience, not inflexibility.</p> <p><strong>B: Pessimism</strong> is also incorrect. In contrast to optimism, pessimism would likely hinder resilience, making it an unsuitable choice.</p> <p><strong>D: Social isolation</strong> is incorrect. The passage mentions that robust social support networks are traits of resilient individuals, indicating that social isolation would not be a characteristic of resilience.</p>"}	\N
TC-1	<History> - <TC-1> - <difficulty-level: 1> - <vocabulary-level:3>	791	2	1	History and Interpretation of Ancient Artifacts	The discovery of ancient artifacts often leads historians to _______ about the cultures that created them.	1	0	0	{}	2025-02-08 05:11:42.779	2025-02-08 05:11:42.779	f	\N	43	t	{"solution": "<p>The correct answer is <b>speculate</b> because historians often make educated guesses about the cultural significance of artifacts based on the evidence available. </p><p>Other options are discussed below:</p><ul><li><b>ignore</b>: This is incorrect as historians actively seek to study artifacts.</li><li><b>confirm</b>: While they may confirm certain aspects, the act of discovering artifacts typically involves speculation more than confirmation.</li><li><b>celebrate</b>: This does not relate to the process of understanding or interpreting artifacts.</li><li><b>wonder</b>: Although historians may wonder about artifacts, it does not fit the context of actively seeking understanding.</li><li><b>document</b>: While documenting is part of their work, it does not capture the interpretive nature of examining cultural artifacts.</li></ul>"}	4
		653	4	2	Implications of Technology on Mental Health	What can be inferred about the relationship between technology and mental health based on the passage?	-1	0	0	{}	2025-02-07 06:47:25.5	2025-02-07 06:47:25.5	t	66	\N	f	{"solution": "<p>The correct answer is <strong>A: Technology can improve access to mental health services for a wider audience.</strong> The passage highlights how digital mental health tools offer accessibility and convenience, suggesting a positive relationship between technology and access to mental health services.</p> <p><strong>B: All digital mental health tools are considered effective and reliable.</strong> This option is incorrect as the passage raises questions about efficacy and potential drawbacks of these tools, indicating that not all are guaranteed to be effective.</p> <p><strong>C: The use of technology in psychology eliminates the need for human therapists.</strong> This statement is incorrect. The passage discusses the role of technology but also emphasizes the importance of human empathy in psychological interventions, indicating that therapists still have a vital role.</p> <p><strong>D: Privacy concerns regarding digital tools are unfounded and negligible.</strong> This is not supported by the passage; rather, it states that privacy concerns are a significant issue that needs consideration, making this option incorrect.</p>"}	\N
		654	4	2	Key Psychological Treatment Approaches	What psychological treatment approach is mentioned in the passage as an example of a paradigm shift?	-1	0	0	{}	2025-02-07 06:47:25.517	2025-02-07 06:47:25.517	t	66	\N	f	{"solution": "<p>The correct answer is <strong>A: Cognitive-Behavioral Therapy</strong>. The passage explicitly mentions this approach as an example of a paradigm shift in psychological treatment, highlighting its emphasis on the interconnectedness of thought patterns, emotions, and behaviors.</p> <p><strong>B: Psychoanalysis</strong> is incorrect. The passage does not mention psychoanalysis as an example of a recent shift in treatment approaches.</p> <p><strong>C: Humanistic Therapy</strong> is also incorrect. This approach is not referenced in the passage as a paradigm shift, so it does not fit the context.</p> <p><strong>D: Gestalt Therapy</strong> is incorrect as well. Similar to the previous options, gestalt therapy is not mentioned in the passage, making it an unsuitable answer.</p>"}	\N
GI	GI - <Finance> - <Critical Thinking> - <Pie Chart> - <difficulty_level: 1>	655	5	2	Budget Allocation Percentages for Departments	The organization allocated __________% of its budget to Research and Development, while __________% was allocated to Operations.	1	0	0	[{"data": [{"label": "Marketing", "value": 25}, {"label": "Research and Development", "value": 35}, {"label": "Human Resources", "value": 20}, {"label": "Operations", "value": 15}, {"label": "IT", "value": 5}], "graph": "pie chart", "title": "Budget Allocation for 2023", "description": "This pie chart illustrates the distribution of an organization's budget for the year 2023 across various departments."}]	2025-02-07 06:47:25.538	2025-02-07 06:47:25.538	f	\N	\N	f	{"solution": "To find the percentages allocated to Research and Development and Operations, we can directly refer to the pie chart data: \\n\\n- The percentage allocated to Research and Development is given as 35\\\\%. \\n- The percentage allocated to Operations is given as 15\\\\%. \\n\\nThus, the answers are: 35\\\\% for Research and Development and 15\\\\% for Operations."}	\N
TA	TA - <Resource Management> - <Comparative Analysis> - <Simple Table> - <Inferred/Conflicting type> - <difficulty_level: 2>	656	5	2	Efficiency Comparison of Resource Allocation across Departments	The table presents the allocation of resources among various departments within a company, highlighting both the percentage of resources allocated and necessary, along with efficiency ratios and performance outcomes. Based on this information, can we infer that the Sales department operates with the highest efficiency ratio compared to the other departments?	2	0	0	{"tables": [{"data": [[30, 25, 20, 15, 5, 5], [25, 30, 25, 10, 5, 5], [1.2, 0.83, 0.8, 1.5, 1, 1], [30000, 25000, 20000, 15000, 5000, 5000], ["Good", "Average", "Average", "Excellent", "Poor", "Poor"]], "rows": ["Row1", "Row2", "Row3", "Row4", "Row5", "Row6"], "columns": [{"Department": ["HR", "Finance", "IT", "Sales", "Marketing", "Operations"]}, {"Resources Allocated (in %)": ["30", "25", "20", "15", "5", "5"]}, {"Resources Needed (in %)": ["25", "30", "25", "10", "5", "5"]}, {"Efficiency Ratio": ["1.2", "0.83", "0.8", "1.5", "1", "1"]}, {"Budget Utilization (in $)": ["30000", "25000", "20000", "15000", "5000", "5000"]}, {"Performance Outcome": ["Good", "Average", "Average", "Excellent", "Poor", "Poor"]}], "table_name": "Resource Allocation Comparison"}]}	2025-02-07 06:47:25.566	2025-02-07 06:47:25.566	f	\N	\N	f	["Option A is incorrect because the Sales department has an efficiency ratio of 1.5, which is actually the highest among all departments.", "Option B is correct as the IT department's efficiency ratio is 0.8, which is lower than Sales but higher than others like Finance and Marketing.", "Option C is incorrect because while the Operations department has an efficiency ratio of 1, it is not close to the Sales department's efficiency ratio of 1.5."]	\N
GI	GI - <Strategy and Management> - <Synthesis of Information> - <Pie Chart> - <difficulty_level: 1>	657	5	2	Budget Allocation Comparison Between Departments	The budget allocated to __________ Marketing is greater than the amount allocated to __________ Human Resources.	1	0	0	[{"data": [{"label": "Marketing", "value": 35}, {"label": "Research & Development", "value": 25}, {"label": "Operations", "value": 20}, {"label": "Human Resources", "value": 10}, {"label": "Sales", "value": 10}], "graph": "pie chart", "title": "Budget Allocation by Department", "description": "This pie chart represents the distribution of the annual budget across various departments within the organization."}]	2025-02-07 06:47:25.593	2025-02-07 06:47:25.593	f	\N	\N	f	{"solution": "To find the budget allocated to Marketing and Human Resources from the pie chart data, we note that the values are as follows: \\\\text{Marketing} = 35\\\\% \\\\text{ and } \\\\text{Human Resources} = 10\\\\%. Thus, we fill in the blanks with the corresponding values. The completed sentence is: The budget allocated to \\\\text{Marketing} is greater than the amount allocated to \\\\text{Human Resources}."}	\N
GI	GI - <Marketing and Sales> - <Quantitative Reasoning> - <Bar Chart> - <difficulty_level: 1>	658	5	2	Comparison of Product A and Product B Sales in Q1	In Q1, the sales of ___________ were ___________ more than the sales of Product B.	1	0	0	[{"data": [{"Q1": 1000, "Q2": 1200, "Q3": 1500, "Q4": 1700, "category": "Product A"}, {"Q1": 800, "Q2": 950, "Q3": 1100, "Q4": 1300, "category": "Product B"}, {"Q1": 600, "Q2": 750, "Q3": 900, "Q4": 1050, "category": "Product C"}], "graph": "bar chart", "title": "Quarterly Sales Data", "x-axis": "Products", "y-axis": "Sales (in USD)", "description": "This chart displays the sales figures of different products over four quarters."}]	2025-02-07 06:47:25.618	2025-02-07 06:47:25.618	f	\N	\N	f	{"solution": "To find the sales of Product A and Product B in Q1:\\n\\n- Sales of Product A in Q1 = \\\\$1000\\n- Sales of Product B in Q1 = \\\\$800\\n\\nNow, we calculate the difference:\\n\\nDifference = Sales of Product A - Sales of Product B = \\\\$1000 - \\\\$800 = \\\\$200\\n\\nThus, the sales of Product A were \\\\$200 more than the sales of Product B."}	\N
GI	GI - <Economics> - <Synthesis of Information> - <Stacked Bar Chart> - <difficulty_level: 2>	659	5	2	Quarterly Revenue Analysis of Product Lines	The total revenue for Q3 is ___________ and for Q4 is ___________.	2	0	0	[{"data": [{"values": [{"value": 5000, "region": "Product A"}, {"value": 3000, "region": "Product B"}, {"value": 2000, "region": "Product C"}], "category": "Q1"}, {"values": [{"value": 6000, "region": "Product A"}, {"value": 4000, "region": "Product B"}, {"value": 3500, "region": "Product C"}], "category": "Q2"}, {"values": [{"value": 8000, "region": "Product A"}, {"value": 5000, "region": "Product B"}, {"value": 4500, "region": "Product C"}], "category": "Q3"}, {"values": [{"value": 9000, "region": "Product A"}, {"value": 5500, "region": "Product B"}, {"value": 5000, "region": "Product C"}], "category": "Q4"}], "graph": "stacked bar chart", "title": "Quarterly Revenue by Product Lines", "x-axis": "Quarters", "y-axis": "Revenue (in USD)", "description": "This chart shows the breakdown of total revenue by different product lines for each quarter."}]	2025-02-07 06:47:25.644	2025-02-07 06:47:25.644	f	\N	\N	f	{"solution": "To find the total revenue for each quarter, we can sum the revenue from all product lines for the specified quarters.\\n\\n1. For Q3:\\n   Total Revenue Q3 = \\text{Revenue of Product A} + \\text{Revenue of Product B} + \\text{Revenue of Product C}\\n   \\\\\\\\;\\n   Total Revenue Q3 = 8000 + 5000 + 4500 = 17500 \\\\\\text{ (in USD)}\\n\\n2. For Q4:\\n   Total Revenue Q4 = \\text{Revenue of Product A} + \\text{Revenue of Product B} + \\text{Revenue of Product C}\\n   \\\\\\\\;\\n   Total Revenue Q4 = 9000 + 5500 + 5000 = 19500 \\\\\\text{ (in USD)}\\n\\nTherefore, the total revenue for Q3 is 17500 and for Q4 is 19500."}	\N
		660	5	2		Based on the Quarterly Sales Data provided, which product had the highest total sales over the four quarters?	1	0	0	{}	2025-02-07 06:47:25.675	2025-02-07 06:47:25.675	t	67	\N	f	{"solution": "The passage discusses how logistics and supply chain companies are adopting technology while considering the associated risks and workforce implications. A critical aspect is how companies can balance technology integration and workforce development. A well-managed transition can yield benefits, while a poorly managed one could cause disruptions. Therefore, the best approach involves understanding both the technological needs and the workforce requirements."}	\N
		661	5	2		Based on the data presented, what is the total sales amount for Product C across all four quarters?	2	0	0	{}	2025-02-07 06:47:25.697	2025-02-07 06:47:25.697	t	67	\N	f	{"solution": "The passage emphasizes the need for companies to adopt a holistic approach when integrating technology into their logistics and supply chain practices. This includes understanding the risks associated with automation and ensuring workforce development to mitigate job displacement. Companies should invest not only in technology but also in training programs for their employees to equip them for new roles. This balanced strategy can help organizations remain competitive while protecting their workforce."}	\N
TA	TA - <Business> - <Critical Reasoning> - <Simple Table> - <Inferred/Conflicting type> - <difficulty_level: 1>	662	5	2	Analysis of Regional Market Share in Product Sales	The table displays the sales data for Product A and Product B across various regions along with the total sales, market share, and growth rate. Based on the sales information, can we conclude which region has the highest market share?	1	0	0	{"tables": [{"data": [[2000, 1500, 3500, 30, 10], [3000, 2000, 5000, 25, 20], [1500, 2500, 4000, 20, 15], [4000, 1000, 5000, 35, 5], [1600, 2400, 4000, 10, 25], [2500, 3000, 5500, 15, 12]], "rows": ["North", "South", "East", "West", "Central", "Northeast"], "columns": ["Region", "Product A Sales", "Product B Sales", "Total Sales", "Market Share (%)", "Growth Rate (%)"], "table_name": "Product Sales by Region"}]}	2025-02-07 06:47:25.718	2025-02-07 06:47:25.718	f	\N	\N	f	["Option A is incorrect because the North region has a market share of 30%, which is not the highest among the regions listed.", "Option B is correct as the South region has a market share of 25%, which, relative to the other regions, is the highest available in the provided data.", "Option C is incorrect because while the West region has a market share of 35%, it is possible that it is inaccurately represented as it should be lower than what we observe in the South region."]	\N
GI	GI - <Economics> - <Pattern Recognition> - <Scatter Plot> - <difficulty_level: 4>	663	5	2	Analyzing Advertising Spend and Sales Revenue Correlation	Based on the scatter plot above, when the advertising spend reaches ___________ USD, the sales revenue is predicted to be ___________ USD.	4	0	0	[{"data": [{"x": 5000, "y": 20000, "label": "Product A"}, {"x": 7000, "y": 30000, "label": "Product B"}, {"x": 4000, "y": 15000, "label": "Product C"}, {"x": 10000, "y": 40000, "label": "Product D"}, {"x": 6000, "y": 25000, "label": "Product E"}], "graph": "scatter plot", "title": "Advertising Spend vs. Sales Revenue", "x-axis": "Advertising Spend (in USD)", "y-axis": "Sales Revenue (in USD)", "description": "This graph illustrates the relationship between advertising spend and corresponding sales revenue for various products."}, {"data": [{"series": "Product A", "values": [{"x": "January", "y": 5000}, {"x": "February", "y": 7000}, {"x": "March", "y": 8000}, {"x": "April", "y": 6000}, {"x": "May", "y": 9000}, {"x": "June", "y": 10000}]}, {"series": "Product B", "values": [{"x": "January", "y": 3000}, {"x": "February", "y": 4000}, {"x": "March", "y": 5000}, {"x": "April", "y": 3500}, {"x": "May", "y": 6000}, {"x": "June", "y": 8000}]}], "graph": "line chart", "title": "Sales Revenue Over Time", "x-axis": "Months", "y-axis": "Sales Revenue (in USD)", "description": "This line chart shows the monthly sales revenue trends for the products over a six-month period."}]	2025-02-07 06:47:25.744	2025-02-07 06:47:25.744	f	\N	\N	f	{"solution": "To solve the question, we will analyze the data from the scatter plot. We can observe the trend to identify the points that relate advertising spend to sales revenue. \\\\n\\\\nLet's calculate the predicted sales revenue when the advertising spend is \\\\$7000. Using the relation from the scatter plot: \\\\n\\\\nFor advertising spend \\\\$7000, sales revenue is approximately \\\\$30000 derived from the data points shown in the graph.\\\\n\\\\nThus, we fill in the blanks as follows:\\\\n\\\\n1. Advertising Spend = 7000 USD\\\\n2. Sales Revenue = 30000 USD\\\\n\\\\nHence the complete statement becomes: Based on the scatter plot above, when the advertising spend reaches \\\\$7000 USD, the sales revenue is predicted to be \\\\$30000 USD."}	\N
GI	GI - <Economics> - <Quantitative Reasoning> - <Line Chart> - <difficulty_level: 1>	664	5	2	Inflation Rate Changes from 2021 to 2022	The inflation rate in 2021 was __________ while the inflation rate in 2022 increased to __________.	1	0	0	[{"data": [{"series": "Inflation Rate", "values": [{"x": "2018", "y": 2.1}, {"x": "2019", "y": 1.8}, {"x": "2020", "y": 1.2}, {"x": "2021", "y": 4.7}, {"x": "2022", "y": 7.0}]}], "graph": "line chart", "title": "Annual Inflation Rate Over Five Years", "x-axis": "Years", "y-axis": "Inflation Rate (%)", "description": "This chart shows the changes in annual inflation rates from 2018 to 2022."}]	2025-02-07 06:47:25.77	2025-02-07 06:47:25.77	f	\N	\N	f	{"solution": "From the line chart, the inflation rate in 2021 is 4.7\\\\% and the inflation rate in 2022 increased to 7.0\\\\%. Therefore, we can write: \\\\text{Inflation Rate in 2021} = 4.7\\\\% \\\\text{ and } \\\\text{Inflation Rate in 2022} = 7.0\\\\%."}	\N
GI	GI - <Budget> - <Attention to Detail> - <Line Chart> - <difficulty_level: 2>	665	5	2	Budget Allocation Trends in Marketing Over Four Years	Based on the line chart, the budget allocation for Digital Marketing in 2022 was ___________ and for TV Advertising in 2023 was ___________.	2	0	0	[{"data": [{"series": "Digital Marketing", "values": [{"x": "2020", "y": 30000}, {"x": "2021", "y": 40000}, {"x": "2022", "y": 50000}, {"x": "2023", "y": 65000}]}, {"series": "TV Advertising", "values": [{"x": "2020", "y": 20000}, {"x": "2021", "y": 25000}, {"x": "2022", "y": 30000}, {"x": "2023", "y": 40000}]}, {"series": "Print Advertising", "values": [{"x": "2020", "y": 15000}, {"x": "2021", "y": 10000}, {"x": "2022", "y": 8000}, {"x": "2023", "y": 5000}]}], "graph": "line chart", "title": "Annual Marketing Budget Allocation Over Time", "x-axis": "Years", "y-axis": "Budget Allocation (in USD)", "description": "This chart illustrates the trend of marketing budget allocation over four consecutive years."}]	2025-02-07 06:47:25.796	2025-02-07 06:47:25.796	f	\N	\N	f	{"solution": "To find the budget allocation for Digital Marketing in 2022 and TV Advertising in 2023, we can refer directly to the values indicated in the line chart. \\\\\\\\text{From the chart:} \\\\\\\\text{Digital Marketing in 2022: } 50000 \\\\\\\\text{TV Advertising in 2023: } 40000. \\\\\\\\text{Thus the values are: } 50000 \\\\text{ and } 40000."}	\N
TA	TA - <Marketing and Sales> - <Data Synthesis> - <Simple Table> - <Acceptable/Not Acceptable type> - <difficulty_level: 2>	666	5	2	Assessment of Sales Performance in the South Region	The table above displays the sales performance by region for each quarter in a year, along with the total sales and the corresponding performance rating (Acceptable/Not Acceptable). Based on the data provided, can we determine if the sales performance in the South region is acceptable based on the total sales figures?	2	0	0	{"tables": [{"data": [[15000, 18000, 21000, 24000, 78000, "Acceptable"], [12000, 15000, 19000, 20000, 66000, "Not Acceptable"], [9000, 11000, 13000, 14000, 49000, "Acceptable"], [16000, 17000, 22000, 25000, 80000, "Acceptable"], [11000, 14000, 16000, 17000, 60000, "Not Acceptable"]], "rows": ["North", "South", "East", "West", "Central"], "columns": [{"Region": ["North", "South", "East", "West", "Central"]}, {"Q1 Sales ($)": [15000, 12000, 9000, 16000, 11000]}, {"Q2 Sales ($)": [18000, 15000, 11000, 17000, 14000]}, {"Q3 Sales ($)": [21000, 19000, 13000, 22000, 16000]}, {"Q4 Sales ($)": [24000, 20000, 14000, 25000, 17000]}, {"Total Sales ($)": [78000, 66000, 49000, 80000, 60000]}, {"Performance Rating": ["Acceptable", "Not Acceptable", "Acceptable", "Acceptable", "Not Acceptable"]}], "table_name": "Marketing and Sales Performance"}]}	2025-02-07 06:47:25.822	2025-02-07 06:47:25.822	f	\N	\N	f	["Option A is 'No' because the total sales in the South region amount to \\\\$66,000, which aligns with the 'Not Acceptable' performance rating indicated in the table.", "Option B is 'Yes' as the total sales figure of \\\\$66,000 for the South region is explicitly marked as 'Not Acceptable' in the performance rating column.", "Option C is 'No' since the performance rating for the South region is 'Not Acceptable', contrary to what this option suggests."]	\N
Data Sufficiency	DS - <Data Sufficiency> - <Critical Reasoning> - <difficulty_level: 1>	667	5	2	Impact of Price Increase on Revenue in a Retail Store	Based on the statements above, can we conclusively determine whether increasing the price per item will always result in increased total revenue?	1	0	0	{"passages": "In a certain retail store, the relationship between the number of items sold (S) and the total revenue generated (R) is governed by the equation R = pS, where p is the price per item. The store owner wants to determine whether increasing the price per item will lead to a proportional increase in total revenue, given that sales data over the past year showed fluctuations caused by seasonal demand changes.", "statements": ["Statement 1: During the summer months, the average price per item sold was $15, while a promotional discount resulted in sales increasing by 30%.", "Statement 2: In the autumn season, the price per item was raised to $20, yet the number of items sold decreased by 25% compared to the previous season."]}	2025-02-07 06:47:25.848	2025-02-07 06:47:25.848	f	\N	\N	f	{"solution": "The statements provide information about price changes and their effects on sales but do not establish a definitive relationship between price increases and total revenue across all seasons. Therefore, while individual scenarios are discussed, we cannot conclude universally that increased prices will always result in higher revenue."}	\N
Data Sufficiency	DS - <Arithmetic> - <Logical Reasoning> - <difficulty_level: 5>	668	5	2	Maximizing Gadget Production Capacity in a Factory Setup	Is it possible for the production capacity of gadgets to exceed 30 units on any given day based on the above statements?	5	0	0	{"passages": "A certain factory produces widgets and gadgets. The production capacity for widgets is given by the equation W = 3X + 7, where X is the number of machines dedicated to widget production. Gadgets are produced using the same machines, but the efficiency decreases based on the equation G = 2(X - 5). Given that the total production of widgets and gadgets is limited to a maximum of 100 units per day, can you determine if the production capacity of gadgets can exceed 30 units on any given day?", "statements": ["Statement (1): The factory has a total of 10 machines available for production.", "Statement (2): On a specific day, the factory produced 50 widgets."]}	2025-02-07 06:47:25.864	2025-02-07 06:47:25.864	f	\N	\N	f	{"solution": "By analyzing Statement (1), if there are 10 machines, W can be calculated as W = 3(10) + 7 = 37, leaving G = 100 - 37 = 63, which exceeds 30. Statement (2) indicates that 50 widgets were produced, hence G = 100 - 50 = 50, which also exceeds 30. Both statements alone suffice to confirm that gadget production can exceed 30 units independently."}	\N
Data Sufficiency	DS - <Word Problems> - <Logical Reasoning> - <difficulty_level: 1>	669	5	2	Workforce Increase and Productivity Relationship	Based on the statements above, can you determine if a 10% productivity increase is achievable solely through a workforce increase?	1	0	0	{"passages": "A company plans to increase its workforce by a certain percentage over the next year. Currently, the company employs 250 workers. The management anticipates that the percentage increase will directly affect productivity, but they are uncertain of the exact relationship between the increase in workforce and the anticipated output. Consequently, they have made plans to either hire additional workers or increase the productivity of current workers. The question remains: what percentage increase in workforce is necessary for the company to achieve an overall productivity increase of at least 10%?", "statements": ["Statement 1: If the workforce is increased by 30%, the productivity of the company is expected to increase by 12%.", "Statement 2: The total productivity of the current workforce, when evaluated over a specific time frame, has historically increased by an average of 8% with a 25% increase in workforce."]}	2025-02-07 06:47:25.88	2025-02-07 06:47:25.88	f	\N	\N	f	{"solution": "Statement 1 alone provides a direct correlation between the percentage increase in workforce and the productivity increase, confirming that a 30% increase in workforce leads to a 12% productivity increase, which covers the company's target of at least 10%. Statement 2, while informative about productivity trends, does not guarantee a solution to the specific inquiry regarding achieving a 10% productivity increase based solely on the given workforce percentage. Therefore, Statement 1 alone is sufficient to determine the answer."}	\N
Data Sufficiency	DS - <Data Sufficiency> - <Efficiency and Time Management> - <difficulty_level: 3>	670	5	2	Retailer Sales Volume Comparison	Is the retailer's total sales volume this year greater than the total sales volume last year?	3	0	0	{"passages": "A certain retailer operates several stores across different states, each with varying sales volumes. The store located in State A has reported a 15% increase in sales over the previous year, while the store in State B has seen a decrease in sales by 10%. The regional manager is interested in determining whether the total sales volume for the retailer this year exceeds the total sales volume from last year across all states.", "statements": ["The sales volume of the store in State A last year was $200,000.", "The total sales volume of the stores in State B and C combined last year was $150,000 and the store in State C has a reported increase of 20%."]}	2025-02-07 06:47:25.897	2025-02-07 06:47:25.897	f	\N	\N	f	{"solution": "Statement (1) alone allows us to calculate the sales volume for State A this year, but without knowing the sales volumes for State B and C or any specific totals, we cannot determine the overall sales volume. Statement (2) provides information about State B and C, but without the specific sales volume from State A or the overall sales volume from last year, we still cannot definitively answer the question. However, combining both statements lets us calculate necessary comparisons of sales volumes, leading to the conclusion about total sales volumes."}	\N
Data Sufficiency	DS - <Data Sufficiency> - <Critical Reasoning> - <difficulty_level: 1>	671	5	2	Equal Funding Distribution for School Science Fair Projects	Is it possible for each student to receive an equal amount of funding for their project if the school has a \\$5,000 budget?	1	0	0	{"passages": "A certain school organizes an annual science fair where students present their projects. Each project requires a specific budget to cover materials, equipment, and other costs. This year's fair is projected to host a maximum of 20 projects. However, the school has a limited budget of \\\\$5,000 for all projects combined. The goal is to determine whether it is feasible for each student to receive an equal amount of funding while adhering to the project's budget constraints.", "statements": ["Statement (1): The average cost per project is estimated to be \\\\$250.", "Statement (2): The school plans to cut down the maximum number of projects to 15."]}	2025-02-07 06:47:25.913	2025-02-07 06:47:25.913	f	\N	\N	f	{"solution": "Both statements indicate how the total budget can be allocated across a varying number of projects. Statement (1) shows that with 20 projects, the funding per project would be \\\\$250, which fits perfectly into the \\\\$5,000 budget. However, statement (2) modifies the situation by reducing the number of projects to 15, where each student would then receive \\\\$333.33, exceeding the budget. Therefore, both statements together affirm that the funding can be equalized, but neither statement alone conclusively determines the feasibility of equal funding under the budget constraints."}	\N
Data Sufficiency	DS - <Data Sufficiency> - <Critical Reasoning> - <difficulty_level: 3>	672	5	2	Determining Bicycle Sales Based on Production and Price	What information is sufficient to determine the number of bicycles sold in the town last month?	3	0	0	{"passages": "In a certain town, the number of bicycles sold in one month (B) is directly proportional to the number of bikes produced (P) in that month and inversely proportional to the average price of each bicycle (A). Accordingly, the relationship can be expressed as B = k * (P/A) where k is a constant. Additionally, it is known that in the last year, the average price of bicycles varied significantly due to market fluctuations. The town council is now interested in determining how many bicycles were sold last month.", "statements": ["Statement (1): The town produced 500 bicycles last month.", "Statement (2): The average price of each bicycle last month was $200."]}	2025-02-07 06:47:25.931	2025-02-07 06:47:25.931	f	\N	\N	f	{"solution": "Both statements together provide a complete picture needed to determine the total bicycles sold, as they give both the production and pricing context, which is crucial given the relationship B = k * (P/A). Alone, neither statement directly provides sufficient information to calculate B."}	\N
Data Sufficiency	DS - <Data Sufficiency> - <Attention to Detail> - <difficulty_level: 2>	673	5	2	Maximizing Production of Type A Gadgets under Constraints	Is it possible for the factory to produce the maximum number of Type A gadgets while meeting both the work hour and type production requirements?	2	0	0	{"passages": "A factory produces two types of gadgets: Type A and Type B. Each Type A gadget requires 3 hours of work and each Type B gadget requires 2 hours of work. The factory has a total of 120 hours available for production in a week. Additionally, there is a rule that at least twice as many Type A gadgets must be produced as Type B gadgets. How many Type A gadgets can the factory produce in a week if these conditions are to be met?", "statements": ["Statement (1): The factory can produce a maximum of 30 Type A gadgets.", "Statement (2): The factory can produce a maximum of 20 Type B gadgets."]}	2025-02-07 06:47:25.947	2025-02-07 06:47:25.947	f	\N	\N	f	{"solution": "Both statements together provide essential information regarding the maximum number of Type A and Type B gadgets that can be produced. Statement (1) indicates that the factory can produce up to 30 Type A gadgets, while Statement (2) indicates that the factory can produce up to 20 Type B gadgets. Using both statements, we can verify whether these quantities meet the production rules (i.e., at least twice as many Type A as Type B) and the total hours available. The calculations confirm that both conditions can be satisfied simultaneously. Therefore, the correct option is C."}	\N
Data Sufficiency	DS - <Algebra> - <Critical Reasoning> - <difficulty_level: 1>	674	5	2	Determining Value of z from Algebraic Expressions	Can the exact value of z be determined from the above statements?	1	0	0	{"passages": "In a certain algebraic expression, let x represent a positive integer and y represent the product of x and two additional consecutive integers. The relationship between x and y is defined by the equation y = x(x + 1)(x + 2). A third integer z is introduced, which is defined as the sum of x, y, and 5. It is necessary to ascertain the specific value of z based solely on the conditions described.", "statements": ["Statement (1): x is equal to 3.", "Statement (2): The result of y when x is 3 leads to z being an even number."]}	2025-02-07 06:47:25.963	2025-02-07 06:47:25.963	f	\N	\N	f	{"solution": "From Statement (1), we have x = 3. Substituting this value into the equation for y gives y = 3(3 + 1)(3 + 2) = 3 * 4 * 5 = 60. Then, z = x + y + 5 = 3 + 60 + 5 = 68. Therefore, Statement (1) alone is sufficient to determine z. Statement (2) states that y leads to z being an even number, but does not provide the necessary value of x or its relation to z directly. Hence, Statement (2) alone is insufficient. Thus, the answer is A: Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient."}	\N
	ChildQuestion: 1 <Critical Reasoning> - <Dicotomous Choice(Acceptable/Not Acceptable)> - <2>	675	5	2	Evaluating the Relationship Between Logistics Costs and Supply Chain Efficiency	Is it acceptable to conclude that higher logistics costs universally lead to lower supply chain efficiency based on the provided data?	2	0	0	{}	2025-02-07 06:47:25.984	2025-02-07 06:47:25.984	t	68	\N	f	{"solution": "To determine if it is acceptable to conclude that higher logistics costs lead to lower supply chain efficiency, we analyze the following: \\n\\nFrom the scatter plot illustrating logistics costs versus supply chain efficiency, we observe varying data points. For example, Company A incurs logistics costs of \\\\$20000 and has a supply chain efficiency of 80\\\\%. In contrast, Company D has higher logistics costs of \\\\$40000 but lower efficiency at 60\\\\%. This suggests some correlation between higher costs leading to lower efficiency. \\n\\nHowever, Company C demonstrates that lower logistics costs of \\\\$15000 coincide with higher efficiency at 90\\\\%. Thus, there are exceptions to the correlation.  \\n\\nAdditionally, the passage indicates that logistics costs can be managed effectively, impacting efficiency positively through optimization strategies. Therefore, while there is evidence supporting a relationship, it does not universally apply to all cases, leading us to conclude that it is **Not Acceptable** to generalize this finding without further evidence for each specific situation. \\n\\nIn summary, conclusions drawn from the data must consider individual company practices and strategies, highlighting the complexity of the logistics cost-efficiency dynamic."}	\N
	ChildQuestion: 2 <Synthesis> - <Dicotomous Choice(Yes/No)> - <1>	676	5	2	Inferring the Impact of Logistics Cost Management on Supply Chain Efficiency	Can it be inferred that effective management of logistics costs positively influences supply chain efficiency based on the combined information from the passages and charts?	1	0	0	{}	2025-02-07 06:47:26.007	2025-02-07 06:47:26.007	t	68	\N	f	{"solution": "To analyze the possibility that effective management of logistics costs positively influences supply chain efficiency, we reference both the passage and the visual data sources. \\n\\nThe passage highlights the significance of managing logistics costs through strategies such as advanced forecasting tools and efficient routing. It states that effective management is crucial for minimizing costs while maximizing supply chain operations.\\n\\nLooking at the provided scatter plot data, we note that Company C, with the lowest logistics costs of \\\\$15000, boasts the highest supply chain efficiency at 90\\\\%. This suggests that lower logistics costs, potentially achieved through effective management, may correlate with higher efficiency in operational practices. \\n\\nAdditionally, the line chart data supports this notion, showing that as companies implement better management practices, trends indicate fluctuations in logistics costs can lead to stable or improved efficiency.\\n\\nThus, we can logically synthesize the information across the sources, concluding that effective management of logistics costs does indeed appear to positively influence supply chain efficiency.\\n\\nTherefore, the answer is **Yes**, effective management of logistics costs correlates with improvements in supply chain efficiency."}	\N
TC-3	<Politics> - <TC-3> - <difficulty-level: 2> - <vocabulary-level:3>	792	2	1	Political Upheaval and Internal Strife	The recent political upheaval in the region has led to a series of changes in leadership, which many analysts argue is not merely a reaction to external pressures but also a result of _______ within the political parties. This internal strife has created a _______ environment, where cooperation is scarce, and has ultimately resulted in _______ governance that struggles to address the needs of the populace.	2	0	0	{}	2025-02-08 05:11:42.807	2025-02-08 05:11:42.807	f	\N	43	t	{"solution": "<p>In this question, **dissension** (A) is correct as it accurately describes the internal conflict within political parties that would lead to upheaval. **Volatile** (F) is suitable for the environment described, indicating instability and unpredictability. **Ineffective** (J) aptly characterizes the governance resulting from this strife.</p> <p>Other options are not suitable because: </p> <ul> <li>**Harmony** (B) contradicts the context of internal conflict.</li> <li>**Resolution** (C) implies a solution, which is not applicable here.</li> <li>**Collaboration** (D) also undermines the idea of internal strife.</li> <li>**Dynamic** (E) does not directly connote instability.</li> <li>**Stable** (G) and **conducive** (H) imply a positive environment, which isn't accurate.</li> <li>**Effective** (I) suggests successful governance, contrary to the scenario's implications.</li> <li>**Robust** (L) implies strength, which doesn't fit the context either.</li> </ul>"}	5
SE	<Science> - <SE> - <difficulty-level: 5> - <vocabulary-level:2>	793	2	1	Significant Discoveries in Science	The discovery of penicillin, which marked a significant milestone in the development of antibiotics, has made many previously deadly infections __________, transforming modern medicine and saving countless lives.	5	0	0	{}	2025-02-08 05:11:42.855	2025-02-08 05:11:42.855	f	\N	43	t	{"solution": "<p><strong>The correct options are B and C:</strong> The sentence indicates that the discovery of penicillin changed previously deadly infections into something that can now be dealt with, which makes 'manageable' and 'preventable' appropriate choices.</p><p><strong>Option A:</strong> 'untreatable' contradicts the context of the sentence as penicillin allowed for treatment.</p><p><strong>Option D:</strong> 'perpetual' does not fit logically, as it suggests ongoing severity rather than improvement.</p><p><strong>Option E:</strong> 'intrusive' does not relate to treatment of infections in this context.</p><p><strong>Option F:</strong> 'isolated' does not align with how infections are managed within the framework of modern medicine.</p>"}	6
RC		794	2	1	Assumptions in Cognitive Distortion Impact	What assumption underlies the premise that cognitive distortions significantly affect emotional responses and behaviors?	3	0	0	{}	2025-02-08 05:11:42.896	2025-02-08 05:11:42.896	t	84	43	t	{"solution": "<p>The correct answer is <strong>C</strong>: 'Thought patterns directly lead to changes in emotional and behavioral responses.' This assumption underlies the concept of cognitive distortions, suggesting that how individuals think directly impacts how they feel and act.</p><p>Option <strong>A</strong> is incorrect because while some cognitive distortions can be recognized, they are often subtle and can be difficult for individuals to identify without guidance.</p><p>Option <strong>B</strong> is incorrect as it contradicts the foundational idea of cognitive psychology, which posits that cognitive processes significantly affect emotional responses.</p><p>Option <strong>D</strong> is also incorrect because it denies the well-established link between thought processes and emotional responses, which is critical in psychological theories and therapies.</p>"}	7
DS	<number theorm>- <difficulty-level: 1>	677	1	1	Exploring Prime Years in a Town's History	Based on the above information, can we determine if the current year is a prime number?	1	0	0	{"passage": "In a small town, the residents are curious about the age of their community park, which was opened in a year that is a prime number. The park was opened exactly 15 years ago. The townsfolk want to find out if the current year is also a prime number. They believe that both prime years are important to their town's history. The current year can be calculated by adding 15 to the year the park was opened.", "statements": ["The year the park was opened is a prime number less than 100.", "The current year is 2022."]}	2025-02-08 04:28:31.995	2025-02-08 04:28:31.995	f	\N	35	t	{"solution": "To determine if the current year is a prime number, we first analyze the statements. Statement (1) tells us that the park opened in a prime year below 100, but without knowing which year this is, we can't directly determine the current year. Statement (2) provides the current year as 2022, which is not a prime number since it can be divided by 1, 2, 1011, and 2022. Therefore, even though we know that the park opened in a prime year, we already know the current year is not prime. Statement (2) alone suffices to answer the question."}	1
DS	<linear inequalities>- <difficulty-level: 1>	678	1	1	Evaluating Apple Tree Growth Limits in a Village Based on Linear Inequalities	Based on the statements above, can the village grow more than 15 apple trees under the given inequality condition?	1	0	0	{"passage": "In a secluded village, the number of apples harvested each season is represented by the inequality 3x + 5y ≤ 60, where x is the number of apple trees and y represents the number of years the trees have been bearing fruit. The elders of the village debated if it's possible to grow more than 15 apple trees while maintaining the harvest below the threshold. The village council decided to evaluate two statements regarding the maximum number of apple trees that can be grown.", "statements": ["If the village grows 15 apple trees, then they must restrict the years of fruit-bearing to 5 or less.", "If the village grows 10 apple trees, there is still some allowance to grow more trees while being within the limit."]}	2025-02-08 04:28:32.084	2025-02-08 04:28:32.084	f	\N	35	t	{"solution": "To determine if the village can grow more than 15 apple trees, we analyze the statements. Statement (1) indicates that with 15 apple trees, the maximum years of fruit-bearing is 5, which gives a strict condition; hence this alone suggests a boundary. In statement (2), if only 10 apple trees are grown, it allows some flexibility, but does not provide a definitive upper limit. Since neither statement alone confirms the possibility of exceeding 15 trees, and combining them also yields no additional constraint, the correct response is that neither statement alone is sufficient to conclude the village can grow more than 15 apple trees. Therefore, the answer is option E."}	2
DS	<linear inequalities>- <difficulty-level: 2>	679	1	1	Public Transportation Policy Compliance: Analyzing Bus and Tram Passenger Ratios	Based on the information provided, is it possible to determine if the local government's transportation policy is being met?	2	0	0	{"passage": "In a certain town, there are two types of public transportation: buses and trams. Buses can carry a maximum of 40 passengers, while each tram can carry 60 passengers. The local government has implemented a new policy that at least twice as many passengers must use buses compared to trams on any given day to reduce traffic congestion. On a particular day, if the number of passengers using buses is represented by `b` and the number of passengers using trams is represented by `t`, which of the following inequalities must hold true?", "statements": ["Statement 1: The number of passengers using buses was 80, and the number of passengers using trams was 40.", "Statement 2: The ratio of bus passengers to tram passengers is at least 2:1."]}	2025-02-08 04:28:32.113	2025-02-08 04:28:32.113	f	\N	35	t	{"solution": "To determine if the local government's transportation policy is being met, we analyze the given statements. Statement 1 provides specific passenger numbers: there are 80 bus passengers and 40 tram passengers. This leads to a ratio of \\\\( \\\\frac{b}{t} = \\\\frac{80}{40} = 2 \\\\), which satisfies the requirement of at least twice as many bus passengers as tram passengers. Therefore, Statement 1 is sufficient alone. Statement 2 states that the ratio of bus passengers to tram passengers is at least 2:1, which also satisfies the policy requirement. However, knowing this alone does not provide specific numbers for `b` and `t`. Consequently, based on those analyses, we conclude: Statement 1 is sufficient to meet the policy, while Statement 2 is not definitive alone. Hence, the correct answer is A: Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient."}	3
NE	<standard deviation and variance>- <difficulty-level: 1>	680	1	1	Calculating the Standard Deviation of Tree Heights in a School Playground	In a peculiar town, a school conducted an experiment by measuring the heights of 10 new trees planted in the playground. The recorded heights in meters are as follows: 3.2, 3.5, 3.8, 3.6, 4.0, 3.9, 3.3, 3.5, 3.7, and 4.1. The principal wants to determine how spread out the heights of these trees are to understand their growth pattern better. Calculate the standard deviation of these heights.	1	0	0	{"answer": 0.28}	2025-02-08 04:28:32.139	2025-02-08 04:28:32.139	f	\N	35	t	{"solution": "<p>Step 1: Calculate the mean height: <br> Mean = (3.2 + 3.5 + 3.8 + 3.6 + 4.0 + 3.9 + 3.3 + 3.5 + 3.7 + 4.1) / 10 = 3.61 <br> <br> Step 2: Calculate each height's deviation from the mean and square it: <br> (3.2 - 3.61)² = 0.1681 <br> (3.5 - 3.61)² = 0.0121 <br> (3.8 - 3.61)² = 0.0361 <br> (3.6 - 3.61)² = 0.0001 <br> (4.0 - 3.61)² = 0.1521 <br> (3.9 - 3.61)² = 0.0841 <br> (3.3 - 3.61)² = 0.0961 <br> (3.5 - 3.61)² = 0.0121 <br> (3.7 - 3.61)² = 0.0081 <br> (4.1 - 3.61)² = 0.2401 <br> <br> Step 3: Average these squared deviations to find the variance: <br> Variance = (0.1681 + 0.0121 + 0.0361 + 0.0001 + 0.1521 + 0.0841 + 0.0961 + 0.0121 + 0.0081 + 0.2401) / 10 = 0.0784 <br> <br> Step 4: Take the square root of the variance to find the standard deviation: <br> Standard Deviation = √0.0784 = 0.28</p>"}	4
MCQ-Multi	<simple interest/compound interest>- <difficulty-level: 2> (multi-correct MCQ)	681	1	1	Calculating Returns from Compound and Simple Interest in Financeonia	In a mystical land called Financeonia, an ancient artifact known as the 'Coin of Compounding' generates interest magically over time. A young scholar invested 500 gold coins into this artifact at an annual interest rate of 8%. If the scholar left the coins to grow for 3 years, he would like to know how much gold he would accumulate by the end of that period. Additionally, concerned about potential risks, he considers an alternative investment opportunity that promises simple interest at the same rate of 8% for the same 3-year timeframe. What are the total amounts he would acquire from both investments at the end of 3 years? Select all correct total amounts.	2	0	0	{}	2025-02-08 04:28:32.145	2025-02-08 04:28:32.145	f	\N	35	t	{"solution": "<p>Compound Interest:<br>Total amount after 3 years = Principal x (1 + Rate) ^ Time<br>Total amount = 500 x (1 + 0.08) ^ 3 = 500 x 1.259712 = ~~629.86~~</p><p>Simple Interest:<br>Total amount after 3 years = Principal x (1 + Rate x Time)<br>Total amount = 500 x (1 + 0.08 x 3) = 500 x (1 + 0.24) = 500 x 1.24 = ~~620.00~~</p>"}	5
MCQ-Multi	<number theorm>- <difficulty-level: 1> (multi-correct MCQ)	682	1	1	Exploring Odd and Even Number Sums in a Mystical Kingdom	In a peculiar kingdom, the King discovers that for every number represented by \\( n \\), if \\( n = 2k + 1 \\) for any integer \\( k \\), then \\( n \\) is considered an odd number. The townsfolk believe in the mystical properties of these odd numbers, which they claim can only form specific sums with even numbers. After gathering the following peculiar numbers: 3, 7, 11, and the first five even numbers: 2, 4, 6, 8, and 10, they conduct a festive competition to see how many distinct sums they can create with one odd number and one even number. Which of the following statements about the sums are accurate? 1) It is possible to achieve a sum of 15. 2) The total number of unique sums that can be formed is 6. 3) No sums can exceed 20.	1	0	0	{}	2025-02-08 04:28:32.16	2025-02-08 04:28:32.16	f	\N	35	t	{"solution": "<p>1. The odd numbers gathered are: [3, 7, 11]. <br> 2. The even numbers are: [2, 4, 6, 8, 10]. <br> 3. We compute the sums by adding each odd number to each even number: <br> - For 3: 3+2=5, 3+4=7, 3+6=9, 3+8=11, 3+10=13 <br> - For 7: 7+2=9, 7+4=11, 7+6=13, 7+8=15, 7+10=17 <br> - For 11: 11+2=13, 11+4=15, 11+6=17, 11+8=19, 11+10=21 <br> 4. The unique sums calculated are: [5, 7, 9, 11, 13, 15, 17, 19, 21]. <br> 5. There are a total of 9 unique sums formed.</p>"}	6
MCQ-Single	<fractions/decimals and Unitary method>- <difficulty-level: 1>	683	1	1	Calculating Revenue and Charity Donation from Apple Pie Sales in a Bakery	In a quaint village, there exists a bakery famous for its delectable pastries. The baker specializes in making apple pies. On a given day, the baker produced 18 apple pies. If each pie is sold at a price of 2.75 dollars, how much total revenue does the baker generate from selling all the pies on that day? Additionally, if the baker decides to donate 1/6 of the total revenue to a local charity, how much money does the charity receive?	1	0	0	{}	2025-02-08 04:28:32.176	2025-02-08 04:28:32.176	f	\N	35	t	{"solution": "<p>Total pies sold = 18 <br> Price per pie = $2.75 <br> Total Revenue = 18 * 2.75 = $49.50 <br> Donation to charity = Total Revenue / 6 = $8.25</p>"}	7
		684	1	1	Estimating Interest Earned Based on Principal Amount	Given the scatter plot illustrating the impact of the principal amount on total interest earned, if a principal amount of $6000 is invested, estimate the total interest earned. Additionally, consider the trend presented in the graph: what would be the interest earned if the principal amount were increased to $7000?	1	0	0	{}	2025-02-08 04:28:32.198	2025-02-08 04:28:32.198	t	69	35	t	{"solution": "For a principal amount of $6000, the estimated total interest earned is $300. For a principal amount of $7000, the estimated total interest earned is approximately $350."}	8
		685	1	1	Estimating Total Gain Based on Rate of Interest	Based on the scatter plot illustrating the effect of the rate of interest on total gain, if an investment generates a total gain of $400 at a rate of 6%, what would be the expected total gain at a rate of 7% considering the trend shown in the graph?	1	0	0	{}	2025-02-08 04:28:32.215	2025-02-08 04:28:32.215	t	69	35	t	{"solution": "For an interest rate of 6%, the estimated total gain is $340. For an interest rate of 7%, the estimated total gain is $400."}	8
		686	1	1	Calculation of Adjusted Fuel Cost Percentage in Logistics Expenses	Based on the data shown in the pie chart illustrating the distribution of logistics costs, if the company aims to reduce fuel costs by 10% while keeping all other expenses constant, what will be the new percentage allocation for fuel costs in the overall logistics expenditure?	1	0	0	{}	2025-02-08 04:28:32.236	2025-02-08 04:28:32.236	t	70	35	t	{"solution": "The new percentage allocation for fuel costs in the overall logistics expenditure after a reduction of 10% is approximately \\\\( 23.08\\\\% \\\\)."}	9
		687	1	1	Forecasting Projected July Expenses in Logistics Operations	In the line graph depicting monthly logistics expenses over a year, if the company predicts a 15% increase in expenses for the month of July compared to the values shown, what will be the projected expenses for July?	1	0	0	{}	2025-02-08 04:28:32.254	2025-02-08 04:28:32.254	t	70	35	t	{"solution": "The projected expenses for the month of July, considering a 15% increase, will be approximately \\\\( 55200 \\\\) USD."}	9
		688	1	1	Calculating New Percentage for Sea Shipping After Redistribution	Referring to the pie chart on the proportion of shipping methods used, if the logistics company aims to increase the share of air shipping by 5% while proportionately reducing the share of sea and land shipping, what will be the new percentage for sea shipping?	1	0	0	{}	2025-02-08 04:28:32.269	2025-02-08 04:28:32.269	t	70	35	t	{"solution": "After increasing the share of air shipping by 5% and proportionately reducing the share of sea shipping, the new percentage for sea shipping will be approximately \\\\( 27.5\\\\% \\\\)."}	9
DS	<linear inequalities>- <difficulty-level: 2>	689	1	1	Food Delivery Time Analysis Using Linear Inequalities	Is the delivery service able to deliver 2 vegetable packages and 3 fruit packages within the given time constraints?	2	0	0	{"passage": "In a simple urban food distribution model, a delivery service uses a linear inequality to determine the maximum number of food packages they can deliver within a specific time frame. The inequality is represented by the equation 3x + 2y ≤ 12, where x represents the number of vegetable packages and y represents the number of fruit packages. Each vegetable package takes 3 minutes to deliver, and each fruit package takes 2 minutes. The manager wishes to know if they can deliver 2 vegetable packages and 3 fruit packages within the allotted time.", "statements": ["The total delivery time for 2 vegetable and 3 fruit packages can be calculated using the delivery service's linear inequality.", "The maximum number of packages deliverable in the given timeframe is specified in terms of x and y."]}	2025-02-08 04:28:32.285	2025-02-08 04:28:32.285	f	\N	36	t	{"solution": "To determine if the delivery service can deliver 2 vegetable packages and 3 fruit packages, we substitute x = 2 and y = 3 into the inequality: 3(2) + 2(3) = 6 + 6 = 12. Since 12 ≤ 12 holds true, Statement (1) alone is sufficient to conclude that the delivery can be made within the time constraints. However, Statement (2) alone does not provide direct information about the specific package numbers. Therefore, the correct answer is option A: Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient."}	1
MCQ-Multi	<number theorm>- <difficulty-level: 2> (multi-correct MCQ)	690	1	1	Exploring Sum-Product Equality in Integer Pairs	In a peculiar town known for its number enthusiasts, a peculiar competition is held annually where participants must find pairs of positive integers that both add and multiply to the same number, dubbed ‘Sum-Product Equality’. For instance, the pair (2,2) has both a sum and product of 4. This year, participants discovered that there are various pairs like (3,1) and (4,0) leading to distinct results. However, after some elaborate calculation and deduction, it was found that two pairs more notably exemplified this phenomenon: (a, b) and (m, n). Participants need to identify which of the following result in the same sum and product, determining the accuracy of their findings. The pairs are: (3,5), (4,2), (6,0), and (1,12). Based on their findings, which of these pairs not only adhere to the established rules but also exemplify the interesting property showcased above?	2	0	0	{}	2025-02-08 04:28:32.312	2025-02-08 04:28:32.312	f	\N	36	t	{"solution": "<p>After evaluating the pairs (3,5), (4,2), (6,0), and (1,12), we find the following results: <br> Pair (3,5): Sum = 3 + 5 = 8, Product = 3 * 5 = 15 <br> Pair (4,2): Sum = 4 + 2 = 6, Product = 4 * 2 = 8 <br> Pair (6,0): Sum = 6 + 0 = 6, Product = 6 * 0 = 0 <br> Pair (1,12): Sum = 1 + 12 = 13, Product = 1 * 12 = 12 <br> None of these pairs lead to a situation where the sum equals the product as both must be equal to the same result.</p>"}	2
DS	<simple interest/compound interest>- <difficulty-level: 1>	691	1	1	Comparing Growth of Simple vs Compound Interest in a Village Librarian's Savings	Is the information provided in the statements sufficient to determine how much more money the librarian will have in the compound interest account compared to the simple interest account after five years?	1	0	0	{"passage": "In a quaint village, a stalwart librarian saved a sum of money from her monthly salary. She decided to invest this money in two different accounts: one yielding simple interest and another accruing compound interest. The simple interest account offered an annual rate of 5%, while the compound interest account compounded yearly at a rate of 6%. After five years, how much more money will she have in the compound interest account compared to the simple interest account if her initial investment was $1000?", "statements": ["The total amount in the simple interest account after five years can be calculated using the formula A = P(1 + rt), where P is the principal, r is the rate, and t is the time in years.", "The total amount in the compound interest account after five years can be determined using the formula A = P(1 + r)^t, where P is the principal, r is the interest rate per period, and t is the number of periods."]}	2025-02-08 04:28:32.328	2025-02-08 04:28:32.328	f	\N	36	t	{"solution": "To determine how much more money the librarian will have in the compound interest account compared to the simple interest account, we can analyze both statements. Statement (1) gives us the method to calculate the amount in the simple interest account, while Statement (2) provides the formula for calculating the amount in the compound interest account. With both formulas, we can independently calculate the amounts: For simple interest, A = 1000(1 + 0.05 * 5) = 1000(1 + 0.25) = 1000 * 1.25 = $1250. For compound interest, A = 1000(1 + 0.06)^5 = 1000(1.41852) ≈ $1418.52. The difference is $1418.52 - $1250 = $168.52, showing that both statements together are sufficient to answer the question. Thus, the answer is option C."}	3
DS	<simple interest/compound interest>- <difficulty-level: 2>	692	1	1	Comparing Savings: Simple vs Compound Interest Accounts	Can Alex determine which account has a greater amount at the end of two years based on the statements provided above?	2	0	0	{"passage": "In a small town, a local bank offers two types of accounts for saving: a simple interest account and a compound interest account. The simple interest account offers an interest rate of 5% per annum, while the compound interest account compounds annually at a rate of 4% per annum. A customer named Alex deposits $1,000 into each account at the beginning of the year. At the end of two years, Alex wishes to compare the total amount accrued in each account. If the total amount is calculated using the formula for simple interest \\\\(A = P(1 + rt)\\\\) and for compound interest \\\\(A = P(1 + r)^t\\\\), can Alex determine which account has a greater amount at the end of the period given the above information?", "statements": ["The total interest earned from the simple interest account after two years is $100.", "The total amount in the compound interest account after two years is $1,081.60."]}	2025-02-08 04:28:32.357	2025-02-08 04:28:32.357	f	\N	36	t	{"solution": "From Statement (1), we know the total interest earned from the simple interest account is $100. Therefore, the total amount in the simple interest account after two years is \\\\(A = 1000 + 100 = 1100\\\\). From Statement (2), the total amount in the compound interest account after two years is $1,081.60. Since $1,100 (simple interest) is greater than $1,081.60 (compound interest), Statement (1) alone is sufficient to determine that the simple interest account has a greater amount than the compound interest account. Therefore, the correct option is A: 'Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient.'"}	4
DS	<permutations and combinations>- <difficulty-level: 2>	693	1	1	Calculating Unique Robot Arrangements in a Robotics Competition	Based on the provided statements, can we determine the total number of unique robot arrangements a team can create for the competition?	2	0	0	{"passage": "In a recent robotics competition, teams were tasked with programming five different robots: A, B, C, D, and E. Each team can select a different combination of these robots to compete in specific challenges, and they can also arrange their sequence of participation. However, they must ensure that each robot is used at least once and no more than twice. The challenge is to determine how many unique arrangements can be made with any selection of robots under these conditions.", "statements": ["The combination of robots selected by a particular team grants them 10 distinct arrangements.", "The team incorporates an additional condition that limits the participation of any robot to no more than once in any given challenge."]}	2025-02-08 04:28:32.382	2025-02-08 04:28:32.382	f	\N	36	t	{"solution": "Statement (1) provides the number of distinct arrangements for a specific selection of robots, which alone is not sufficient to determine the overall arrangements since it does not account for variations in combinations. Statement (2) adds a restriction that may affect the total arrangements but lacks the complete setup needed without information on how many robots are chosen. Thus, neither statement alone suffices. When both statements are considered, they also do not provide a clear calculation method or complete insight into the total arrangements without knowing the original combinations. Therefore, the correct answer is option E: Statements (1) and (2) TOGETHER are NOT sufficient."}	5
MCQ-Multi	<permutations and combinations>- <difficulty-level: 2> (multi-correct MCQ)	694	1	1	Calculating Combinations and Permutations at a Carnival Game Event	In a peculiar carnival, there are 4 distinct booths offering a variety of games: a ring toss, a dart throw, a balloon pop, and a spinning wheel. Each of these booths has an equal probability of participants winning prizes. For a special event, the carnival allows participants to play any 2 games of their choice from the booths without replacement, and they must choose distinct games. What are the total different combinations in which participants can select their games? Additionally, if the carnival decides to award bonus points for selecting the games in a specific order, how many different permutations can participants utilize for selecting these two games, assuming that the order matters? Identify all the viable combinations and permutations that would make one eligible for bonus points in this scenario.	2	0	0	{}	2025-02-08 04:28:32.41	2025-02-08 04:28:32.41	f	\N	36	t	{"solution": "<p>To determine the total number of combinations of selecting 2 games from 4 distinct booths, we can use the combination formula: C(n, k) = n! / (k!(n-k)!). Here, n is the total number of booths (4), and k is the number of games to be selected (2). Therefore, <br>  <b>Combinations:</b> C(4, 2) = 4! / (2!(4-2)!) = (4 × 3) / (2 × 1) = 6. <br> Additionally, to calculate the number of permutations for those 2 games, we use the permutation formula: P(n, k) = n! / (n-k)!. Therefore, <br> <b>Permutations:</b> P(4, 2) = 4! / (4-2)! = 4 × 3 = 12. <br> Hence, there are a total of 6 combinations and 12 permutations available for participants.</p>"}	6
NE	<profit, loss and discount>- <difficulty-level: 2>	695	1	1	Calculating Profit from a Discounted Tuna Sale at a Coastal Fish Market	In a small coastal town, a family-run fish market offers a unique promotion for its fresh catch. The market sells tuna at a price of $25 per kilogram. To attract more customers, the owner decides to provide a 20% discount on the price of the tuna during the weekend. Despite this discount, the owner maintains that the cost price of the tuna is $18 per kilogram. If the market sells 150 kilograms of tuna over the weekend, what will be the total profit earned by the owner after applying the discount?	2	0	0	{"answer": 300.0}	2025-02-08 04:28:32.425	2025-02-08 04:28:32.425	f	\N	36	t	{"solution": "<p>Selling Price per kg = $25 <br> Discount = 20% <br> Discount Amount = ~~20% of $25 = $5~~ <br> Selling Price after Discount = ~~$25 - $5 = $20~~ <br> Total Revenue from 150 kg = ~~150 kg * $20 = $3000~~ <br> Cost Price per kg = $18 <br> Total Cost for 150 kg = ~~150 kg * $18 = $2700~~ <br> Total Profit = Total Revenue - Total Cost = ~~$3000 - $2700 = $300~~ </p>"}	7
NE	<probability>- <difficulty-level: 2>	696	1	1	Probability of Selecting Ruby Stones from a Set of Enchanted Stones	In a mystical realm, a sorcerer possesses a peculiar set of enchanted stones, each with a high probability of granting fortune. The sorcerer has 12 stones: 3 are ruby (representing good luck), 5 are emerald (symbolizing wisdom), and 4 are sapphire (embodying mystery). If the sorcerer randomly selects 4 stones without replacement, what is the probability that exactly 2 of the selected stones will be ruby? Assume that the selection is made in a way that the fate of the realm hinges on this decision.	2	0	0	{"answer": 0.22}	2025-02-08 04:28:32.431	2025-02-08 04:28:32.431	f	\N	36	t	{"solution": "<p>Number of ways to choose 2 ruby stones from 3 = C(3, 2) = 3 <br> Number of ways to choose 2 non-ruby stones from 9 (5 emerald + 4 sapphire) = C(9, 2) = 36 <br> Total ways to choose 4 stones from 12 = C(12, 4) = 495 <br> Thus, the probability of selecting exactly 2 ruby stones = (C(3, 2) * C(9, 2)) / C(12, 4) = (3 * 36) / 495 = 0.22</p>"}	8
		697	1	1	Identifying the Department with the Highest Employee Turnover Rate	Given the information from the bar graph illustrating the employee turnover rates across various departments, if the overall turnover rate for the organization is 12%, which department exhibits the highest turnover, and by how much does it exceed the organizational average?	1	0	0	{}	2025-02-08 04:28:32.442	2025-02-08 04:28:32.442	t	71	36	t	{"solution": "The department with the highest turnover rate is Human Resources, with a turnover rate of 20%. To calculate how much this exceeds the overall organizational average turnover rate of 12%, we subtract the average from the departmental rate: \\\\(20\\\\% - 12\\\\% = 8\\\\%\\\\). Therefore, the Human Resources department's turnover rate exceeds the organizational average by 8\\\\%."}	9
		698	1	1	Analyzing Employee Satisfaction Across Departments	Referring to the bar graph depicting employee satisfaction scores by department, determine which department has the lowest satisfaction score and what percentage lower it is compared to the department with the highest satisfaction score. Additionally, calculate the average satisfaction score across all departments.	1	0	0	{}	2025-02-08 04:28:32.457	2025-02-08 04:28:32.457	t	71	36	t	{"solution": "The department with the lowest satisfaction score is Human Resources (HR) with a score of 50, while the department with the highest score is Information Technology (IT) with a score of 80. The percentage difference between these two departments is \\\\(80 - 50 = 30\\\\). Additionally, the average satisfaction score across all departments is \\\\(67.0\\\\)."}	9
		699	1	1	Evaluating Recruitment Success Rates by Source	Based on the bar graph representing recruitment success rates by source, identify the recruitment source with the highest success rate, and calculate how much more effective it is compared to the source with the lowest success rate. Furthermore, determine the overall average success rate across all sources.	1	0	0	{}	2025-02-08 04:28:32.473	2025-02-08 04:28:32.473	t	71	36	t	{"solution": "The recruitment source with the highest success rate is Referrals, achieving a rate of 80, while the source with the lowest success rate is Social Media, with a rate of 20. The effectiveness difference between these two sources is \\\\(80 - 20 = 60\\\\). Furthermore, the overall average success rate across all sources is \\\\(55.0\\\\)."}	9
		700	1	1	Analyzing Experiment 2's Probability of Success and Overall Average	In the study of various experiments, a highlight table presents their respective probabilities of success. Considering the information provided, what is the probability of success for Experiment 2, and how does it compare to the highest probability recorded among all experiments? Additionally, calculate the average probability for all experiments listed in the table to understand the overall success rate in this study.	1	0	0	{}	2025-02-08 04:28:32.494	2025-02-08 04:28:32.494	t	72	36	t	{"solution": "The probability of success for Experiment 2 is 0.39. The highest probability recorded among all experiments is 0.86. The average probability for all experiments is 0.52."}	10
		701	1	1	Cumulative Probability and Comparison with Average Success Rate	Given the highlight table and the associated probabilities of success for different experiments, what is the cumulative probability of success for all experiments combined, and how does that compare to the average probability of individual experiments? Additionally, identify which experiment(s) had a probability greater than the average probability calculated.	1	0	0	{}	2025-02-08 04:28:32.509	2025-02-08 04:28:32.509	t	72	36	t	{"solution": "The cumulative probability of success for all experiments combined is 2.58. This is compared to the average probability of 0.52 for individual experiments. The following experiment(s) had a probability greater than the average: Experiment 1, Experiment 5."}	10
		702	1	1	Projected Employee Turnover in the Sales Department	Given the turnover rates listed in the table for each department, what would be the projected number of employees who are expected to leave in the Sales department if the total number of employees remains the same for the upcoming year?	1	0	0	{}	2025-02-08 04:28:32.53	2025-02-08 04:28:32.53	t	73	36	t	{"solution": "In the Sales department, with a turnover rate of 15%, the projected number of employees expected to leave is \\\\( 7.5 \\\\) employees."}	11
		703	1	1	Combined Budget Allocation for Sales and Marketing Departments	Based on the average salary data provided in the second table, what would be the total budget allocation in percentage allotted to the Sales and Marketing departments combined?	1	0	0	{}	2025-02-08 04:28:32.546	2025-02-08 04:28:32.546	t	73	36	t	{"solution": "The combined budget allocation for the Sales and Marketing departments is \\\\( 45\\\\% \\\\)."}	11
TC-1	<Politics> - <TC-1> - <difficulty-level: 4> - <vocabulary-level:1>	704	2	1	Politics and Transparency	In the political arena, the need for transparency has become increasingly _______ as citizens demand more accountability from their leaders.	4	0	0	{}	2025-02-08 04:28:32.564	2025-02-08 04:28:32.564	f	\N	37	t	{"solution": "<p><strong>urgent</strong> is the correct option because it conveys the importance of transparency in politics amidst rising citizen demands. The other options do not fit within the context:</p><ul><li><strong>superfluous</strong>: suggests something unnecessary, which contradicts the context.</li><li><strong>optional</strong>: implies it is not required, also incorrect.</li><li><strong>discreet</strong>: does not relate to the context of public transparency.</li><li><strong>beneficial</strong>: while positive, it does not express the necessity indicated.</li><li><strong>arcane</strong>: means secret and obscured, which is the opposite of what is being discussed.</li></ul>"}	1
TC-2	<Psychology> - <TC-2> - <difficulty-level: 1> - <vocabulary-level:2>	705	2	1	Psychology: Behavioral and Mental Factors	The study of psychology often involves examining the intricate relationship between behavior and _______ factors, while also taking into account the _______ aspects that can influence an individual's mental state.	1	0	0	{}	2025-02-08 04:28:32.603	2025-02-08 04:28:32.603	f	\N	37	t	{"solution": "<p>In this question, the correct options are <b>environmental</b> and <b>sociocultural</b>. These factors play a crucial role in shaping behavior and mental states, reflecting how outside influences can affect psychological processes.</p> <p>Other option discussions:</p> <ul><li><b>cognitive</b>: While cognitive factors are relevant, they are more about internal mental processes rather than external influences.</li><li><b>physical</b>: This option pertains to bodily states but does not encompass the broader psychological influences.</li><li><b>genetic</b>: Although genetics can impact behavior, it does not directly relate to the environmental aspect.</li><li><b>emotional</b>: Emotions are indeed significant, but they stem from psychological responses rather than acting as external factors.</li><li><b>psychological</b>: This is a redundant term in the context, as it does not specify the external influences at play.</li><li><b>biological</b>: Similar to genetic, biological factors are more about intrinsic properties rather than environmental interactions.</li></ul>"}	2
TC-3	<Philosophy> - <TC-3> - <difficulty-level: 2> - <vocabulary-level:2>	706	2	1	Philosophical Inquiry and the Nature of Reality	In the realm of philosophical inquiry, many thinkers have proposed that the nature of reality is not merely a physical construct, but rather an intricate tapestry woven from _______ experiences, _______ perceptions, and _______ interpretations that challenge our conventional understanding of existence.	2	0	0	{}	2025-02-08 04:28:32.643	2025-02-08 04:28:32.643	f	\N	37	t	{"solution": "<p>In this question, the correct answers are <b>subjective</b>, <b>emotional</b>, and <b>metaphysical</b>. These terms effectively illustrate how personal experiences, feelings, and abstract concepts intertwine to shape our understanding of reality.</p> <p><b>Option A (subjective)</b>: This option highlights the importance of personal perspective in interpreting reality.</p> <hr> <p><b>Option E (emotional)</b>: This emphasizes the role of feelings in shaping our view of existence.</p> <hr> <p><b>Option I (metaphysical)</b>: This points to broader philosophical ideas beyond physical existence.</p> <hr> <p>Other options like <b>objective</b> and <b>materialist</b> don't fit since they focus more on external, physical, or universally accepted truths rather than individual experiences.</p>"}	3
TC-3	<Economics> - <TC-3> - <difficulty-level: 1> - <vocabulary-level:1>	707	2	1	Complexities of Market Function in Economics	In traditional economics, the concept of supply and demand is often used to explain how markets function. However, this model can be overly simplistic and may not account for the complexities involved in real-world transactions where factors such as consumer behavior, market structures, and external influences can create __________. In such scenarios, it is essential to recognize that market equilibrium is often not achieved, leading to __________ and potentially ________ economic instability.	1	0	0	{}	2025-02-08 04:28:32.694	2025-02-08 04:28:32.694	f	\N	37	t	{"solution": "<p>The correct options in the sentence are <strong>A</strong> (fluctuations), <strong>F</strong> (deficits), and <strong>I</strong> (severe). Thus, the completed sentence reads: '...creating fluctuations. In such scenarios, it is essential to recognize that market equilibrium is often not achieved, leading to deficits and potentially severe economic instability.'</p><p>Explanation of options:</p><ul><li><strong>A</strong> (fluctuations) is the appropriate choice as it captures the unpredictable nature of real-world transactions.</li><li><strong>F</strong> (deficits) is fitting here since failing to achieve equilibrium often results in deficits in markets.</li><li><strong>I</strong> (severe) describes the type of economic instability that can arise, emphasizing the seriousness of the situation.</li></ul><p>Other options in their respective groups do not fit as well:</p><ul><li><strong>B</strong> (harmony), <strong>C</strong> (predictability), <strong>D</strong> (balance) suggest an overly simplistic or ideal situation that is not reflective of real market conditions.</li><li><strong>E</strong> (surpluses), <strong>G</strong> (equities), <strong>H</strong> (stability) do not directly relate to the outcomes of a market that is not in equilibrium.</li><li><strong>J</strong> (minimal), <strong>K</strong> (temporary), <strong>L</strong> (chronic) imply varying degrees or types of issues but lack the impactful emphasis required in the context of the sentence.</li></ul>"}	4
SE	<Science> - <SE> - <difficulty-level: 2> - <vocabulary-level:3>	708	2	1	Science and Technology Support	Despite the initial skepticism surrounding the new technology, the results are beginning to show __________ support from users, indicating a potential shift in public perception.	2	0	0	{}	2025-02-08 04:28:32.742	2025-02-08 04:28:32.742	f	\N	37	t	{"solution": "<p>The correct options are <strong>unequivocal</strong> and <strong>resounding</strong> as both suggest strong, clear support for the new technology, aligning with the context of a potential positive shift in public perception.</p> <p><strong>Option B</strong> (ambivalent) is incorrect because it implies mixed feelings, which contradicts the idea of growing support. <br> <strong>Option C</strong> (marginal) denotes minimal support, which does not fit the context of increasing acceptance. <br> <strong>Option D</strong> (mixed) also suggests a lack of clear support. <br> <strong>Option E</strong> (tentative) implies uncertainty, which is not applicable here.</p>"}	5
RC		709	2	1	Challenging the Viability of Universal Basic Income	Which of the following, if true, would most seriously weaken the argument that universal basic income (UBI) is a viable solution for poverty alleviation?	1	0	0	{}	2025-02-08 04:28:32.787	2025-02-08 04:28:32.787	t	74	37	t	{"solution": "<p>The correct option is <strong>D</strong> because if long-term studies reveal that UBI can discourage people from seeking employment, it undermines the argument that UBI is a viable solution for poverty alleviation, as a primary goal of UBI is to empower people to achieve economic stability through work.</p><p>Option <strong>A</strong> is incorrect because if studies indicate that UBI has led to increased work participation, it would actually support the argument that UBI is a good policy.</p><p>Option <strong>B</strong> is also incorrect since the belief that UBI can foster creative entrepreneurship would bolster the argument that UBI could be beneficial by allowing individuals the financial flexibility to innovate.</p><p>Lastly, option <strong>C</strong> is incorrect because higher consumer spending as a result of UBI would not weaken the argument; instead, it would indicate a potential economic benefit of the program.</p>"}	6
RC		710	2	1	Assessing the Impacts of Globalization on Economic Equality	Which of the following conclusions can be drawn from the discussions around globalization and its impact on economic inequalities?	4	0	0	{}	2025-02-08 04:28:32.812	2025-02-08 04:28:32.812	t	74	37	t	{"solution": "<p>The correct option is <strong>B</strong> because the passage indicates that the benefits of globalization are often distributed unevenly, favoring developed nations while exacerbating inequalities in developing regions. This aligns with the discussions presented regarding globalization's impacts.</p><p>Option <strong>A</strong> is incorrect since the passage explicitly states that the benefits of globalization are not universally experienced, contradicting the conclusion that it benefits all nations equally.</p><p>Option <strong>C</strong> is incorrect because although protectionist policies are becoming more common, the passage does not claim that they are universally accepted as the best solution to economic disparities; instead, it discusses a growing backlash against globalization.</p><p>Lastly, option <strong>D</strong> is incorrect as the passage implies that technological advancements have introduced complexities into globalization, and therefore they do affect the dynamics of the phenomenon.</p>"}	6
RC		711	2	1	Understanding Economic Policies through Public Perception	Based on the passages, what can be inferred about the relationship between economic policies and public perception?	3	0	0	{}	2025-02-08 04:28:32.839	2025-02-08 04:28:32.839	t	74	37	t	{"solution": "<p>The correct option is <strong>B</strong> because the passages indicate that economic policies, such as globalization and universal basic income, are facing backlash when they do not address public concerns and sentiments. This suggests that policies that ignore public perception may not be sustainable.</p><p>Option <strong>A</strong> is incorrect as the passage does not support the idea that public perception is always in alignment with government policies; rather, it highlights the potential for discord.</p><p>Option <strong>C</strong> is also incorrect since the passage implies that public perception can influence the effectiveness and acceptance of economic policies, suggesting some level of impact.</p><p>Lastly, option <strong>D</strong> is incorrect because the passages do not state that economic policies are primarily successful with global consensus; rather, they discuss the complexities and challenges of globalization without focusing on global agreement as a prerequisite for success.</p>"}	6
RC		712	2	1	Inferring the Impact of Early Development on Emotional Well-Being	Based on the passages, which of the following statements can be inferred about the relationship between emotional well-being and early psychological development?	5	0	0	{}	2025-02-08 04:28:32.869	2025-02-08 04:28:32.869	t	75	37	t	{"solution": "<p>The correct option is <strong>B</strong>: Positive early relationships can enhance later emotional health. This conclusion is supported by the passage discussing attachment theory, which indicates that early attachments between infants and caregivers significantly affect emotional well-being throughout life.</p><p>Option <strong>A</strong> is incorrect because the passages indicate that early psychological experiences do influence later emotional well-being.</p><p>Option <strong>C</strong> is incorrect as well, as it suggests an exclusive reliance on genetic factors, ignoring the substantial role environmental influences play in emotional development.</p><p>Lastly, option <strong>D</strong> is also incorrect because it implies that all individuals have similar emotional outcomes, disregarding the critical impact of individual experiences in early development.</p>"}	7
RC		713	2	1	Unpacking the Core Focus of Psychological Study	What is the primary focus of the passages regarding the field of psychology?	5	0	0	{}	2025-02-08 04:28:32.893	2025-02-08 04:28:32.893	t	75	37	t	{"solution": "<p>The correct option is <strong>B</strong>: The exploration of various subfields and their contributions to understanding human behavior. This focus is evident throughout the passages, which discuss diverse areas such as cognitive psychology, developmental psychology, and positive psychology and their roles in comprehending psychological phenomena.</p><p>Option <strong>A</strong> is incorrect because while mental disorders are mentioned, they are not the primary focus of the passages overall.</p><p>Option <strong>C</strong> is also incorrect, as the passages do not prioritize the role of technology in psychological research; rather, they concentrate on theoretical and practical aspects of psychology.</p><p>Lastly, option <strong>D</strong> is incorrect since, although historical aspects are touched upon, the main emphasis is on various psychological subfields and their contemporary relevance rather than their historical evolution.</p>"}	7
RC		714	2	1	Examining the Underlying Assumptions in Positive Psychology	What assumption underlies the findings in positive psychology discussed in the passages?	2	0	0	{}	2025-02-08 04:28:32.929	2025-02-08 04:28:32.929	t	75	37	t	{"solution": "<p>The correct option is <strong>A</strong>: Individuals have the capacity to change their psychological state through intentional practices. This assumption underlies the principles of positive psychology, suggesting that people can enhance their well-being through interventions like gratitude journaling and mindfulness meditation.</p><p>Option <strong>B</strong> is incorrect because it limits the effectiveness of positive psychology to certain disorders, when, in fact, it aims to foster general well-being across all individuals.</p><p>Option <strong>C</strong> is also incorrect, as it implies a deterministic view of human behavior, which contradicts the premise of positive psychology that emphasizes individual agency and change.</p><p>Lastly, option <strong>D</strong> is incorrect because it suggests that happiness is entirely externally driven, while positive psychology emphasizes that internal practices can significantly influence well-being.</p>"}	7
RC		715	2	1	Identifying the Central Theme of Integrated Psychological Subfields	What central theme is illustrated by the integration of different subfields of psychology as discussed in the passages?	5	0	0	{}	2025-02-08 04:28:32.962	2025-02-08 04:28:32.962	t	75	37	t	{"solution": "<p>The correct option is <strong>A</strong>: The diversity of psychological approaches enhances the understanding of human behavior. This central theme is reflected throughout the passages, which highlight how various subfields contribute different insights and methodologies, leading to a more comprehensive understanding of psychology.</p><p>Option <strong>B</strong> is incorrect because it suggests that psychological subfields do not interact or influence one another, which contradicts the passages' emphasis on integrating approaches for better understanding.</p><p>Option <strong>C</strong> is incorrect as it implies a sole focus on biological factors, whereas the passages also discuss cognitive, developmental, and social aspects of psychology.</p><p>Lastly, option <strong>D</strong> is incorrect because it suggests a uniformity in treatment methodologies across all psychological theories, while the passages indicate a variety of therapeutic approaches stemming from different subfields.</p>"}	7
TC-2	<Economics> - <TC-2> - <difficulty-level: 2> - <vocabulary-level:1>	716	2	1	Behavioral Economics and Decision-Making	In recent years, the field of behavioral economics has gained considerable traction, challenging traditional theories that assume individuals are always ______ when making decisions about spending and saving. Proponents argue that these new perspectives provide a more ______ understanding of economic behavior, incorporating cognitive biases and emotional influences.	2	0	0	{}	2025-02-08 04:28:32.99	2025-02-08 04:28:32.99	f	\N	38	t	{"solution": "<p><strong>A</strong> is correct because behavioral economics proposes that individuals do not always act rationally when making financial decisions, supporting the premise of the sentence.</p><p> For the second blank, <strong>E</strong> is accurate as it suggests a more detailed understanding of economic behavior by considering factors like cognitive biases.</p><p> Other options:</p><ul><li><strong>B</strong> (impulsive) does not fit the context of typical decision-making in economics.</li><li><strong>C</strong> (logical) contradicts the idea presented in behavioral economics.</li><li><strong>D</strong> (conservative) is not relevant to understanding modern economic behavior.</li></ul><p><strong>F</strong> (simplistic) and <strong>G</strong> (conventional) do not capture the complex nature of behavioral economics, and <strong>H</strong> (fragmented) fails to convey a coherent understanding.</p>"}	1
SE	<Philosophy> - <SE> - <difficulty-level: 2> - <vocabulary-level:1>	717	2	1	Philosophical Argument and Nuanced Contributions	The philosopher's argument was not only compelling but also ________; it was evident that he had meticulously considered opposing viewpoints, enhancing the depth of his reasoning. ________ contributions to the discourse ensured that the discussion remained nuanced and reflective.	2	0	0	{}	2025-02-08 04:28:33.03	2025-02-08 04:28:33.03	f	\N	38	t	{"solution": "<p>The correct options are <b>impartial</b> and <b>pertinent</b>. The term <i>impartial</i> highlights the philosopher's ability to present a balanced argument, while <i>pertinent</i> underscores the relevance of his contributions to the discourse.</p><hr/><p>Other options are not suitable because: </p><ul><li><b>irrelevant</b>: This implies that the argument had no connection to the discussions, which contradicts the context.</li><li><b>unbiased</b>: While it suggests fairness, it is not as strong as <i>impartial</i> in indicating the depth of consideration for opposing views.</li><li><b>superficial</b>: This indicates a lack of depth, which is contrary to the description of the argument as compelling.</li><li><b>perfunctory</b>: This suggests only a minimal effort was made, which also contradicts the idea of a nuanced discussion.</li></ul>"}	2
TC-1	<Politics> - <TC-1> - <difficulty-level: 1> - <vocabulary-level:3>	718	2	1	Politics - Public Response to New Policy	Despite the political unrest, the new policy was met with an unexpectedly ______ response from the public.	1	0	0	{}	2025-02-08 04:28:33.057	2025-02-08 04:28:33.057	f	\N	38	t	{"solution": "<p>The correct answer is <b>enthusiastic</b> because it indicates a positive and energetic response from the public, which aligns with the context of the sentence. </p><p>Other options discussion:</p><ul><li><b>hostile</b>: This suggests a negative reaction, conflicting with the idea of an unexpected positive response.</li><li><b>indifferent</b>: This implies a lack of interest, which does not fit with the notion of a response.</li><li><b>supportive</b>: While positive, it does not convey the same level of excitement as 'enthusiastic'.</li><li><b>apathy</b>: Similar to indifferent, it denotes a lack of concern, which is not suitable.</li><li><b>derisive</b>: This reflects mockery or scorn, clearly opposite to a positive response.</li></ul>"}	3
RC		795	2	1	Understanding the Core of Social Psychology	What is the main idea of the passage regarding social psychology?	2	0	0	{}	2025-02-08 05:11:42.93	2025-02-08 05:11:42.93	t	84	43	t	{"solution": "<p>The correct answer is <strong>B</strong>: 'Social psychology examines how individuals are influenced by the presence of others.' This encapsulates the main idea of the passage, highlighting the field's focus on the interaction between individual behavior and social contexts.</p><p>Option <strong>A</strong> is incorrect because it misrepresents social psychology, which does not focus solely on individual cognitive processes but rather emphasizes the social context in shaping behavior.</p><p>Option <strong>C</strong> is incorrect, as while prejudice and discrimination are important topics, they do not encompass the entirety of social psychology.</p><p>Option <strong>D</strong> is also incorrect because it overlooks the significance of group dynamics, which are fundamental to understanding social influence.</p>"}	7
TC-3	<Science> - <TC-3> - <difficulty-level: 4> - <vocabulary-level:1>	719	2	1	Quantum Mechanics and the Elusiveness of Fundamental Principles	The groundbreaking research in quantum mechanics has offered us profound insights into the activity of subatomic particles, yet the underlying _______ of these phenomena remains elusive to many scientists, often leading to a fragmentary understanding. As researchers delve deeper, they continually strive to uncover the _______ principles that govern the behavior of these particles, hoping to unify _______ theories into a cohesive framework.	4	0	0	{}	2025-02-08 04:28:33.087	2025-02-08 04:28:33.087	f	\N	38	t	{"solution": "<p>The correct options are <b>nature</b>, <b>fundamental</b>, and <b>competing</b>.</p><p><u>Explanation:</u></p><p>The use of <b>nature</b> in the first blank appropriately conveys the core identity or essence of quantum mechanics phenomena, which remains challenging to grasp.</p><p><b>fundamental</b> fits in the second blank, indicating that researchers are searching for the basic, foundational principles that explicate the behavior of subatomic particles.</p><p><b>competing</b> theories in the final blank suggest that there are various theories that have yet to be consolidated into a single framework, which aligns with current scientific discourse.</p><hr><p><b>Complexity</b> is not suitable since it doesn’t fit the concept of “underlying” in the first blank.</p><p><b>superficial</b> implies a lack of depth, which contradicts the scientific aim to uncover insights.</p><p><b>unique</b> does not reference foundational principles, making it less relevant.</p><p><b>misleading</b> conveys an incorrect connotation about scientific principles.</p><p><b>contradictory</b> and <b>empirical</b> do not fit well with the context of searching for coherent theories, which strive towards unity.</p><p><b>abstract</b> may pertain to theoretical constructs but lacks the immediate relevance to the search for fundamental principles.</p>"}	4
TC-1	<Literature> - <TC-1> - <difficulty-level: 1> - <vocabulary-level:2>	720	2	1	Protagonist's Symbolism in Literature	The novel's protagonist is often seen as a(n) _______ figure, embodying the struggles and aspirations of a generation.	1	0	0	{}	2025-02-08 04:28:33.135	2025-02-08 04:28:33.135	f	\N	38	t	{"solution": "<p><strong>Option A</strong> is correct because the term 'heroic' aligns with the description of a protagonist who represents struggles and aspirations. It highlights the positive attributes typically associated with a central character in literature.</p><hr/><p><strong>Option B</strong> ('antagonistic') contradicts the idea of a protagonist, as an antagonist is usually a foe in the narrative.</p><hr/><p><strong>Option C</strong> ('mundane') suggests a lack of significance, which does not fit a character embodying struggles and aspirations.</p><hr/><p><strong>Option D</strong> ('tragic') could relate to certain protagonists but does not encompass the broader sense of embodying aspirations.</p><hr/><p><strong>Option E</strong> ('mythical') implies an unrealistic persona that may not represent a generation's struggles effectively.</p><hr/><p><strong>Option F</strong> ('insignificant') directly opposes the notion of embodying struggles and aspirations, marking it as an incorrect choice.</p>"}	5
TC-1	<History> - <TC-1> - <difficulty-level: 2> - <vocabulary-level:1>	721	2	1	Economic Insights from Ancient Civilizations	The study of ancient civilizations reveals that they were often characterized by a (_______) understanding of commerce and trade.	2	0	0	{}	2025-02-08 04:28:33.166	2025-02-08 04:28:33.166	f	\N	38	t	{"solution": "<p>The correct answer is <b>comprehensive</b> because ancient civilizations often had a thorough understanding of commerce and trade that enabled them to establish complex economic systems. </p><p>Other options explained:</p><ul><li><b>superficial</b>: suggests a shallow understanding, which does not align with the advanced trade practices of many ancient societies.</li><li><b>limited</b>: implies a restricted view, contradicting the evidence of extensive trade networks.</li><li><b>chaotic</b>: indicates disorder, which is not representative of the organized nature of historical trade systems.</li><li><b>primitive</b>: suggests a very basic level of understanding, which is an inaccurate description of sophisticated ancient economies.</li><li><b>narrow</b>: implies a lack of depth, which does not reflect the complexity found in ancient commerce.</li></ul>"}	6
RC		722	2	1	Exploring the Underlying Themes of Regret and Dreams	What underlying themes are portrayed through the characters of Stevens in `The Remains of the Day` and Jay Gatsby in `The Great Gatsby`?	5	0	0	{}	2025-02-08 04:28:33.204	2025-02-08 04:28:33.204	t	76	38	t	{"solution": "<p>The correct answer is <strong>A</strong>: Both characters experience profound loneliness as a consequence of their devotion to unattainable ideals.</p><p>Option <strong>A</strong> is accurate because both Stevens and Gatsby sacrifice meaningful relationships in their pursuit of their respective dreams, leading to a deep sense of isolation.</p><p>Option <strong>B</strong> misrepresents the themes; while Stevens is devoted to duty, he does not embody triumph, but rather tragedy, and Gatsby's success is superficial and ultimately hollow.</p><p>Option <strong>C</strong> is incorrect as both characters face disillusionment; they do not achieve fulfillment through their aspirations, but instead find emptiness.</p><p>Option <strong>D</strong> oversimplifies the narratives; while status and wealth are significant, the core of their journeys highlights the cost of neglecting personal connections.</p>"}	7
RC		723	2	1	The Impact of Setting on Themes of Regret and the American Dream	How do the settings in `The Remains of the Day` and `The Great Gatsby` enhance the themes of regret and the American Dream respectively?	5	0	0	{}	2025-02-08 04:28:33.225	2025-02-08 04:28:33.225	t	76	38	t	{"solution": "<p>The correct answer is <strong>B</strong>: Stevens' English estate symbolizes lost opportunities, while Gatsby's lavish parties represent the emptiness of wealth.</p><p>Option <strong>B</strong> is correct as it directly relates the settings to the characters' internal conflicts; Stevens' estate is a reminder of his emotional confinement, while Gatsby's parties showcase the superficial allure of his wealth.</p><p>Option <strong>A</strong> is incorrect because the settings do not reflect success and happiness; rather, they reveal deeper themes of regret and disillusionment.</p><p>Option <strong>C</strong> mistakenly attributes a rural landscape to both novels; while setting is key, it is not accurately described for `The Great Gatsby` which is distinctly urban.</p><p>Option <strong>D</strong> is partly true but lacks specificity; though settings highlight inner turmoil, they are primarily tied to themes of regret and materialism.</p>"}	7
RC		796	2	1	Assumptions About Early Childhood Experiences	What assumption is made about early childhood experiences in the context of developmental psychology?	4	0	0	{}	2025-02-08 05:11:42.948	2025-02-08 05:11:42.948	t	84	43	t	{"solution": "<p>The correct answer is <strong>B</strong>: 'Early interactions with caregivers have a lasting impact on emotional development.' This assumption is central to developmental psychology and underlines the importance of foundational relationships in shaping emotional and social capacities.</p><p>Option <strong>A</strong> is incorrect as it completely disregards the significance of early experiences, which are widely recognized as crucial in influencing later behavior.</p><p>Option <strong>C</strong> is incorrect because it simplifies developmental processes, which are often non-linear and influenced by a variety of factors.</p><p>Option <strong>D</strong> is also incorrect because it fails to acknowledge the diversity of individual experiences, which can vary greatly depending on environmental and contextual factors.</p>"}	7
RC		724	2	1	Exploring the Foundations of Ancient Achievements	What primary factors contributed to the advancements in governance and architecture in ancient civilizations as discussed in the passages?	1	0	0	{}	2025-02-08 04:28:33.25	2025-02-08 04:28:33.25	t	77	38	t	{"solution": "<p>The correct answer is <strong>B: Innovations in engineering and civic participation</strong>. The passages emphasize how advancements in engineering, as showcased by the construction of pyramids in Egypt and Roman infrastructure, played a crucial role in shaping ancient societies. Additionally, the civic participation seen in Athens' democratic practices contributed to the development of governance.</p><p>Option <strong>A: The presence of written language and military strength</strong> is partially correct; while written language, like cuneiform, was important, military strength alone does not comprehensively address the contributions to governance and architecture.</p><p>Option <strong>C: Religious beliefs and trade relations</strong> do feature in ancient civilizations, but they are not the primary factors highlighted in the passages regarding advancements in governance and architecture.</p><p>Option <strong>D: Geographic location and population density</strong> may influence civilization developments, but the passages focus more specifically on engineering and civic engagement as direct contributors to achievements in governance and architecture.</p>"}	8
RC		725	2	1	The Impact of Ancient Political Systems on Modern Governance	How did the political systems of ancient Greece and Rome influence modern governance structures?	2	0	0	{}	2025-02-08 04:28:33.272	2025-02-08 04:28:33.272	t	77	38	t	{"solution": "<p>The correct answer is <strong>A: They established the concept of democracy and citizenship rights.</strong> The passages highlight how ancient Greece, particularly Athens, is credited with developing early democratic principles, where citizens had a role in decision-making, which directly influences modern democratic ideals and the notion of citizenship.</p><p>Option <strong>B: They emphasized the importance of divine rule over human governance</strong> is inaccurate in this context, as neither ancient Greece nor Rome predominantly focused on governance as divinely mandated, especially in the cases discussed in the passages.</p><p>Option <strong>C: They introduced the idea of a monarchy as the preferred political structure</strong> is misleading. While monarchies existed, the focus of the passages is on democratic systems rather than monarchies as a political structure.</p><p>Option <strong>D: They demonstrated that governance can be based solely on military strength</strong> is also incorrect. Although military power was a factor in ancient empires, the passages emphasize civic participation and the establishment of laws and governance systems as the foundations of their political structures, rather than purely military dominance.</p>"}	8
RC		726	2	1	Cultural Achievements and Governance in Ancient Civilizations	What can be inferred about the relationship between cultural achievements and governance in ancient civilizations based on the passages?	5	0	0	{}	2025-02-08 04:28:33.291	2025-02-08 04:28:33.291	t	77	38	t	{"solution": "<p>The correct answer is <strong>B: Governance played a vital role in fostering cultural achievements.</strong> The passages indicate that structured political systems, such as democracy in Greece and the administrative frameworks of Rome, were integral in supporting and facilitating cultural advancements and innovations, including architecture and philosophy.</p><p>Option <strong>A: Cultural achievements often were independent of political structures</strong> is not supported by the passages, as they show a clear link between the stability provided by governance and the flourishing of cultural achievements.</p><p>Option <strong>C: Ancient civilizations prioritized military achievements over cultural developments</strong> is misleading. While military strength was a component of governance, the passages focus on the intersections of governance and cultural contributions rather than stating that one was prioritized over the other.</p><p>Option <strong>D: The lack of written language hindered cultural advancements</strong> does not apply in this context. In fact, the introduction of written language, as indicated in the passages, was a significant factor that facilitated cultural achievements rather than hindered them.</p>"}	8
RC		727	2	1	Understanding the Core Themes of Contemporary Political Dynamics	What is the main idea conveyed in the passages regarding the current state of politics?	3	0	0	{}	2025-02-08 04:28:33.316	2025-02-08 04:28:33.316	t	78	38	t	{"solution": "<p>The correct answer is <strong>C</strong>: The interplay of media, ideology, and globalization shapes modern political landscapes. This option encapsulates the various themes discussed in the passages, highlighting how these elements interact to influence political dynamics.</p><p><strong>A:</strong> The rise of technology has completely replaced traditional political institutions. This statement is inaccurate as technology has not replaced these institutions but rather transformed their functionality and engagement with the public.</p><p><strong>B:</strong> Globalization has led to a more isolated national identity among countries. While there is tension resulting from globalization, the premise that it leads to isolation contradicts the fundamental nature of globalization, which connects nations.</p><p><strong>D:</strong> Populism is the only political movement influencing contemporary politics. This is misleading as the passages suggest a variety of movements and ideological shifts are at play, rather than attributing influence to populism alone.</p>"}	9
RC		728	2	1	Inferences on Media's Influence in Politics	What can be inferred about the role of media in shaping public perception of political issues based on the passages?	5	0	0	{}	2025-02-08 04:28:33.336	2025-02-08 04:28:33.336	t	78	38	t	{"solution": "<p>The correct answer is <strong>B</strong>: Misinformation can significantly distort public understanding of political realities. This option aligns with the discussions in the passages regarding the challenges posed by the prevalence of false narratives in the digital age.</p><p><strong>A:</strong> Media has no significant impact on public perception of political issues. This statement is incorrect as the passages emphasize the crucial role media plays in shaping how political issues are perceived.</p><p><strong>C:</strong> Media only serves as a platform for government propaganda. This is a narrow view that overlooks the diversity of media sources and the critical role of independent journalism in informing the public.</p><p><strong>D:</strong> Social media eliminates the role of traditional media in political discourse. This is misleading; while social media has transformed engagement, traditional media still retains an important place in political discourse alongside new platforms.</p>"}	9
RC		729	2	1	Assumptions About Voter Behavior in a Digital Age	What underlying assumption can be made about the political behavior of voters in the current media landscape based on the passages?	4	0	0	{}	2025-02-08 04:28:33.356	2025-02-08 04:28:33.356	t	78	38	t	{"solution": "<p>The correct answer is <strong>A</strong>: Voters possess the ability to critically evaluate information from multiple sources. This assumption is reflected in the passages that emphasize the importance of media literacy in navigating the complex information landscape.</p><p><strong>B:</strong> All voters are equally informed regardless of the media they consume. This is not a reasonable assumption as the passages suggest significant disparities in access to accurate information due to varying media sources.</p><p><strong>C:</strong> Voters are predominantly influenced by traditional media outlets. While traditional media still plays a role, the passages indicate that social media and digital platforms have also become critical in shaping political perceptions.</p><p><strong>D:</strong> Misinformation is unlikely to affect voter behavior in elections. This statement underestimates the potential impact of misinformation, as the passages highlight how false narratives can distort public understanding and influence voter decisions.</p>"}	9
RC		730	2	1	Connecting Themes of Globalization, Media, and Ideology in Politics	What overarching theme connects the discussions of globalization, media influence, and political ideology in the passages?	3	0	0	{}	2025-02-08 04:28:33.375	2025-02-08 04:28:33.375	t	78	38	t	{"solution": "<p>The correct answer is <strong>B</strong>: Political discourse is increasingly shaped by the interplay of various global and local influences. This response effectively captures the essence of the passages, which discuss how globalization, media, and ideology interact to influence politics.</p><p><strong>A:</strong> The decline of traditional political parties is the sole outcome of globalization. This is an oversimplification, as globalization has various influences, and the decline of traditional parties is just one aspect.</p><p><strong>C:</strong> Media is irrelevant in shaping ideological beliefs within globalization. This statement is inaccurate; the passages highlight the significant role media plays in conveying ideological viewpoints, especially in a global context.</p><p><strong>D:</strong> Voter apathy is the main challenge faced by modern democracies. While voter apathy is a concern, it is not the central theme discussed in the passages, which focus more on the dynamics of influence among globalization, media, and ideology.</p>"}	9
RC		797	2	1	Empiricism: The Foundation of Knowledge	Which philosophical perspective asserts that knowledge is primarily derived from sensory experience?	5	0	0	{}	2025-02-08 05:11:42.973	2025-02-08 05:11:42.973	t	85	43	t	{"solution": "<p>The correct answer is <strong>A: Empiricism</strong>. This philosophical perspective emphasizes that knowledge is primarily derived from sensory experience, affirming that our understanding of the world is shaped by observation and interaction with our environment.</p><p><strong>B: Rationalism</strong> is incorrect because it holds that reason and innate ideas, rather than sensory experience, are the key sources of knowledge.</p><p><strong>C: Existentialism</strong> is not applicable here, as it primarily addresses individual existence and the creation of meaning rather than the acquisition of knowledge.</p><p><strong>D: Utilitarianism</strong> focuses on the consequences of actions and their ability to promote happiness, which does not pertain to the source of knowledge.</p>"}	8
RC		798	2	1	Existentialism: The Essence of Individuality and Freedom	What is the primary focus of existentialist philosophy as discussed in the passage?	3	0	0	{}	2025-02-08 05:11:42.997	2025-02-08 05:11:42.997	t	85	43	t	{"solution": "<p>The correct answer is <strong>B: The creation of identity through choices</strong>. This option accurately reflects the existentialist belief that individuals are not born with a predetermined nature but instead forge their identities through their actions and decisions.</p><p><strong>A: The preordained nature of individuals</strong> is incorrect as existentialism specifically argues against the idea that individuals have a set essence at birth.</p><p><strong>C: Conformity to societal norms</strong> is not in alignment with existentialist philosophy, which often critiques such conformity as a barrier to authentic existence.</p><p><strong>D: The importance of intellectual reasoning</strong> misrepresents the focus of existentialism, which prioritizes freedom and personal responsibility over pure reasoning as seen in rationalist thought.</p>"}	8
RC		799	2	1	Kantian Ethics: The Basis of Moral Duty	What assumption underlies the Kantian ethical framework discussed in the passage?	3	0	0	{}	2025-02-08 05:11:43.019	2025-02-08 05:11:43.019	t	85	43	t	{"solution": "<p>The correct answer is <strong>B: Ethical behavior is based on universal maxims</strong>. This assumption is central to Kant's deontological ethics, which posits that moral actions should be guided by principles that could be applied universally, regardless of the results.</p><p><strong>A: Moral actions are determined by their consequences</strong> is incorrect as it describes utilitarianism, not Kantian ethics, which focuses on duty over outcomes.</p><p><strong>C: Personal desires should guide moral decisions</strong> contradicts Kant's emphasis on duty and the importance of adhering to moral law rather than subjective desires.</p><p><strong>D: Happiness is the ultimate goal of morality</strong> does not align with Kantian ethics, which prioritizes adherence to duty rather than the pursuit of happiness as in utilitarian philosophy.</p>"}	8
TC-1	<History> - <TC-1> - <difficulty-level: 1> - <vocabulary-level:1>	800	2	1	History and Cultural Transition	The Renaissance was a period of great cultural and intellectual _______ in Europe, marking a transition from the medieval to the modern world.	1	0	0	{}	2025-02-08 05:11:43.043	2025-02-08 05:11:43.043	f	\N	44	t	{"solution": "<p>The correct answer is <b>revival</b>, as the Renaissance is characterized by a significant revival of arts and learning in Europe.</p><ul><li><b>decline</b>: This option is incorrect because the Renaissance was not a period of decline but rather a flourishing of culture.</li><li><b>stagnation</b>: Stagnation suggests a lack of progress, which does not accurately describe the Renaissance.</li><li><b>confusion</b>: This option implies disorder, contrasting sharply with the clarity and creativity of the period.</li><li><b>chaos</b>: Chaos is not applicable, as the Renaissance involved organized cultural advancements.</li><li><b>disruption</b>: While there were conflicts, the overall impact of the Renaissance was not one of disruption but of renewal.</li></ul>"}	1
MCQ-Single	<Real Contextual> - <Word Problems> - <Obtaining the best answer(which has confusing options, luring the user to choose the wrong one)> - <Trial and Error Method(type of questions)> - <Resource Management> - <difficulty_level: 3>	731	3	2	Budget Allocation for Printer Supplies in a Resource-Management Scenario	A company produces a specialized printer that consumes a certain amount of ink per printed page. The company has a budget of $5,000 to allocate for ink and other printing supplies for the upcoming quarter. The cost of ink cartridges is $30 each, and each cartridge produces an average of 300 pages. Additionally, the company has decided to provide each employee with basic printing supplies at a cost of $10 per employee per month. If there are 20 employees, and they will be working for three months during this quarter, how many printer cartridges can the company purchase while still covering the costs of the supplies for its employees, and what is the maximum number of pages that can be printed? Consider that all expenses must fit within the budget. Use this data to extrapolate the information; remember to configure your calculations step by step, as it's easy to overlook costs.	3	0	0	{}	2025-02-08 05:07:53.472	2025-02-08 05:07:53.472	f	\N	39	t	{"solution": "To solve the problem, we first calculate the total cost allocated for employee supplies over three months. Given that each employee costs $10 per month, for 20 employees working for three months, the total employee cost calculates as follows: \\\\( 10 \\\\times 20 \\\\times 3 = 600 \\\\). Thus, the total costs for employees is $600. Next, we subtract this from the company\\\\'s budget of $5,000 to find the remaining budget for printer cartridges: \\\\( 5000 - 600 = 4400 \\\\). With the remaining budget, we need to find out how many cartridges can be purchased at $30 each: \\\\( \\\\frac{4400}{30} = 146.67 \\\\). Since the company can only purchase whole cartridges, they can buy 146 cartridges. Each cartridge produces 300 pages, resulting in a total of printed pages: \\\\( 146 \\\\times 300 = 43800 \\\\). Therefore, the company can allocate budget efficiently to print a total of 43,800 pages while ensuring all related expenses are accounted for."}	1
MCQ-Single	<Pure Contextual> - <Arithmetic> - <Number Sense> - <Rates> - <difficulty_level: 3>	732	3	2	Impact of Population Changes on Coffee Enthusiasts in a Small Town	In a peculiar town, the population of coffee enthusiasts is estimated to be 20% of the total population. Recently, the coffee lovers' club started a campaign that aimed to increase the number of coffee enthusiasts by 15% over a period of six months. Simultaneously, the council issued a directive that the total population of the town should decrease by 10% by the end of the same period due to a new housing regulation. If the current population of the town is 10,000 residents, what will be the final count of coffee enthusiasts after the campaign and the population reduction, assuming the percentage of coffee enthusiasts remains consistent throughout these changes?	3	0	0	{}	2025-02-08 05:07:53.523	2025-02-08 05:07:53.523	f	\N	39	t	{"solution": "To determine the final count of coffee enthusiasts after both the campaign and the population reduction, we first need to calculate the current number of coffee enthusiasts in the town. The total population is 10,000, and the coffee enthusiasts make up 20% of this population.\\n\\n1. **Calculate Current Coffee Enthusiasts**:  \\n   Current Coffee Enthusiasts = Total Population * Percentage of Coffee Enthusiasts  \\n   = 10,000 * 0.20 = 2,000.\\n\\n2. **Calculate New Coffee Enthusiasts After Campaign**:  \\n   The campaign aims to increase the number of coffee enthusiasts by 15%.  \\n   New Coffee Enthusiasts = Current Coffee Enthusiasts * (1 + Increase Percentage)  \\n   = 2,000 * (1 + 0.15) = 2,000 * 1.15 = 2,300.\\n\\n3. **Calculate New Total Population After Reduction**:  \\n   The town's population will decrease by 10% due to housing regulations.  \\n   New Population = Total Population * (1 - Decrease Percentage)  \\n   = 10,000 * (1 - 0.10) = 10,000 * 0.90 = 9,000.\\n\\n4. **Calculate Final Coffee Enthusiasts Based on New Population**:  \\n   Final Coffee Enthusiasts = New Population * Percentage of Coffee Enthusiasts  \\n   = 9,000 * 0.20 = 1,800.\\n\\nThus, the final count of coffee enthusiasts after taking into account the campaign and the population reduction will be 1,800."}	2
MCQ-Single	<Pure Contextual> - <Word Problems> - <Assessing given Situation(checking the ability of accessing a given situation)> - <Rates> - <Taxation> - <difficulty_level: 1>	733	3	2	Calculating Total Cost of Pastries Including Tax in a Local Bakery	In a small town, a local bakery sells a variety of pastries. The bakery charges a base price of $2.00 for each pastry. Recently, they introduced a tax that adds an additional rate of 5% to the total cost of the pastries. If a customer walks into the bakery and decides to buy 5 pastries, what will be the total amount the customer has to pay, including the tax?	1	0	0	{}	2025-02-08 05:07:53.579	2025-02-08 05:07:53.579	f	\N	39	t	{"solution": "To find the total amount the customer has to pay for the pastries including tax, we proceed as follows: First, calculate the total price before tax by multiplying the base price per pastry ($2.00) by the number of pastries (5). This gives us a total price of $10.00. Next, we need to find the total tax amount by applying the tax rate of 5%. We calculate 5% of $10.00, which equals $0.50. Finally, we add the tax amount to the total price before tax: $10.00 + $0.50 equals $10.50. Therefore, the total amount the customer has to pay is $10.50."}	3
MCQ-Single	<Real Contextual> - <Algebra> - <Backsolving> - <Inequalities> - <difficulty_level: 1>	734	3	2	Maximizing the Purchase of Apples within a Budget	Anna is planning to buy some fruits for her weekly grocery. She visits a local market where apples are sold for x dollars per kilogram. If the total money Anna has is not less than 10 dollars, which of the following inequalities represents the maximum number of kilograms of apples Anna can buy from the market? Consider that she wants to purchase whole kilograms of apples.	1	0	0	{}	2025-02-08 05:07:53.631	2025-02-08 05:07:53.631	f	\N	39	t	{"solution": "To determine how many kilograms of apples Anna can buy, we start with the inequality representing her budget against the price of apples. If x is the price of apples per kilogram and Anna has at least 10 dollars, the inequality can be expressed as:  \\n\\nx * k ≤ 10  \\n\\nwhere k is the number of kilograms of apples. To find the maximum value of k, we rearrange the inequality:  \\n\\nk ≤ 10/x  \\n\\nThus, k must be less than or equal to 10 divided by the price per kilogram (x). Since k represents whole kilograms, we need to find the largest integer value that satisfies this condition based on the value of x."}	4
MCQ-Single	<Real Contextual> - <Arithmetic> - <Critical Reasoning> - <Unitary Method> - <difficulty_level: 2>	735	3	2	Sales Calculation of Bakeries A and B: A Comparative Analysis	In a small town, bakery A produces 120 loaves of bread every day, while bakery B produces 150 loaves of bread daily. Bakery A has recently begun to offer a discount to increase sales. The bakery offers a discount of 10% on each loaf of bread. On the other hand, bakery B has increased its production capacity by 20% to meet the rising demand for its bread. If bakery A sells 75% of its loaves daily after applying the discount, and bakery B sells all its loaves, what is the total number of loaves sold by both bakeries in a day?	2	0	0	{}	2025-02-08 05:07:53.681	2025-02-08 05:07:53.681	f	\N	39	t	{"solution": "To determine the total number of loaves sold by both bakeries in a day, we first calculate the number of loaves sold by each bakery. Bakery A produces 120 loaves of bread and offers a 10% discount on each loaf. The selling price after the discount becomes $0.90 per loaf. After applying the discount, Bakery A sells 75% of its loaves. Therefore, the number of loaves sold by Bakery A is calculated as: 120 loaves * 0.75 = 90 loaves.\\n\\nFor Bakery B, the bakery originally produces 150 loaves daily. With a 20% increase in production, bakery B now produces: 150 loaves * 1.20 = 180 loaves. Since it sells all of its loaves, the total loaves sold by Bakery B is 180.\\n\\nFinally, we sum the loaves sold by both bakeries: 90 loaves (Bakery A) + 180 loaves (Bakery B) = 270 loaves. Thus, the total number of loaves sold by both bakeries in a day is 270."}	5
MCQ-Single	<Pure Contextual> - <Arithmetic> - <Number Sense> - <Discount, Profit and Loss> - <difficulty_level: 4>	736	3	2	Calculating the Potent Savings in the Enchanted Marketplace	In a remote, mystical marketplace known for its enchanted artifacts, the vendor has set the following prices for a selection of unique items. A potion of immortality is initially priced at 240 gold coins, but the vendor offers a discount of 15% for anyone who purchases the potion along with a magical scroll priced at 160 gold coins. However, if a customer decides not to buy the scroll, the potion will only be available at a 5% discount. If a clever merchant buys both the potion and scroll, yet later decides to return the scroll, how many gold coins would he have saved or lost by returning the scroll instead of retaining both items? Assume there is a return fee of 10% of the scroll's price that applies if the scroll is returned. Calculate the total amount the merchant spends in both scenarios and determine the difference between the two amounts.	4	0	0	{}	2025-02-08 05:07:53.73	2025-02-08 05:07:53.73	f	\N	39	t	{"solution": "In the mystical marketplace, if the merchant buys the potion and the scroll together, the discounted price of the potion becomes 240 - (240 * 0.15) = 240 - 36 = 204 gold coins. Therefore, the total cost when buying both the potion and the scroll is 204 + 160 = 364 gold coins. If the merchant decides to return the scroll, he incurs a return fee of 10% of the scroll's price, which is 160 * 0.10 = 16 gold coins. Consequently, the residual cost after returning the scroll would be the cost of the potion plus the cost of the scroll after the return fee, which is 204 + (160 - 16) = 204 + 144 = 348 gold coins. Thus, the merchant ends up saving 364 - 348 = 16 gold coins by opting to return the scroll instead of retaining both items."}	6
MCQ-Single	<Pure Contextual> - <Algebra> - <Backsolving> - <Inequalities> - <difficulty_level: 1>	737	3	2	Maximizing Attendance under a Fitness Class Inequality	In a recent study conducted by a local community center, it was found that the number of people attending a fitness class can be represented by the inequality 2x + 3y < 15. If the average attendance of people was 5 and a new promotion is introduced that increases attendance by 5 people, what is the maximum number of people that can attend the fitness class without violating the inequality?	1	0	0	{}	2025-02-08 05:07:53.787	2025-02-08 05:07:53.787	f	\N	39	t	{"solution": "To solve the inequality 2x + 3y < 15, we start by substituting the known value of x, which represents the average attendance of 5. The equation becomes: 2(5) + 3y < 15. Therefore, simplifying the left side gives us 10 + 3y < 15. Next, we subtract 10 from both sides, resulting in 3y < 5. Dividing both sides by 3 yields y < 1.67. However, since the attendance must be a whole number, the maximum integer value for y is 1. This indicates that without violating the inequality, the maximum number of people that can attend the fitness class after considering the increase of 5 due to promotion is 1."}	7
MCQ-Single	<Real Contextual> - <Word Problems> - <Choosing correct mathematical tools to solve problems(Questions which may have 2 or more mathematical approachs to solve, but user would have to choose the most optimal and efficient approach: generate question content in that manner)> - <Work and Time> - <Finance> - <difficulty_level: 5>	738	3	2	Comparative Analysis of Two Investment Strategies Over a 5-Year Period	In a bustling metropolitan area, a financial analyst is tasked with evaluating the efficiency of two different investment strategies for managing a portfolio. Strategy A involves a high-frequency trading model that operates continuously throughout the trading day, while Strategy B uses a traditional buy-and-hold approach with periodic rebalancing. It's known that Strategy A has a potential for a 15% return per annum due to its frequent trades, but it incurs operational costs equivalent to 3% of the total investment amount each year. On the other hand, Strategy B, while enjoying a lower return of 8% per annum, has significantly lower costs that amount to only 0.5% of the total investment amount. The analyst decides to invest a total sum of $200,000, comparing the net returns from both strategies over a duration of 5 years. Given that the portfolio allows for the reinvestment of returns, calculate the returns generated by both strategies. Which investment strategy yields the highest net return at the end of the period? Furthermore, assess whether the choice of strategy would have been different if the operational cost of Strategy A increased to 5%. Provide a comprehensive analysis, factoring in all possible scenarios and the implications of each approach on the total returns over the specified period.	5	0	0	{}	2025-02-08 05:07:53.831	2025-02-08 05:07:53.831	f	\N	39	t	{"solution": "To determine the net returns from both investment strategies over a 5-year period, we can analyze each strategy step by step. For Strategy A, which offers a 15% annual return but incurs a 3% operational cost, we calculate the net growth over the investment period. The effective return per year after accounting for costs is (15% - 3%) = 12%. Therefore, the growth factor over 5 years is (1 + 0.12)^5.\\\\n\\\\nCalculating this gives us a final investment amount of approximately $352,468.34 for Strategy A.\\\\n\\\\nFor Strategy B, we have an 8% return with a 0.5% operational cost. The net effective return here becomes (8% - 0.5%) = 7.5%, leading to a growth factor of (1 + 0.075)^5 over the same period. Consequently, the final amount from Strategy B comes out to approximately $287,125.87.\\\\n\\\\nThe difference in returns between the two strategies is approximately $65,342.47, indicating that Strategy A indeed yields the highest net return after 5 years.\\\\n\\\\nTo further assess the scenario whereby the operational cost of Strategy A increases to 5%, recalculating the effective return for Strategy A becomes essential. The new effective return would be (15% - 5%) = 10%. Plugging this into the growth factor formula yields a final investment amount. Comparing this revised amount with Strategy B will confirm if the choice of strategy would change under the new cost conditions."}	8
MCQ-Single	<Real Contextual> - <Algebra> - <Number Picking(by logical and critical reasoning over constraints given in the question)> - <Functions> - <difficulty_level: 4>	739	3	2	Maximizing Profit from Chicken Crunch Sandwich Sales at Tasty Bites	In a bustling city, a popular food truck, 'Tasty Bites,' sells three types of sandwiches: Veggie Delight, Chicken Crunch, and Beef Blast. The owner notices that the profit from sandwiches is modeled by the equation P(x) = -2x^2 + 16x - 24, where P represents the profit in dollars and x is the number of Chicken Crunch sandwiches sold. According to the city’s newest health regulations, Tasty Bites is only allowed to sell between 0 and 10 Chicken Crunch sandwiches in a day. What is the maximum profit the food truck can achieve from selling Chicken Crunch sandwiches, considering the stated constraints?	4	0	0	{}	2025-02-08 05:07:53.873	2025-02-08 05:07:53.873	f	\N	39	t	{"solution": "To maximize the profit from the sales of Chicken Crunch sandwiches, we first identify the profit function given as P(x) = -2x^2 + 16x - 24. This is a quadratic function, and since the coefficient of x^2 is negative, the parabola opens downwards, indicating the presence of a maximum profit. The maximum profit can be found at the vertex of the parabola. The x-coordinate of the vertex can be calculated using the formula x = -b/(2a), where a and b are the coefficients from the standard form of the quadratic equation ax^2 + bx + c. Here, a = -2 and b = 16. Thus, we find x = -16/(2*(-2)) = 4. To find the maximum profit, we substitute x = 4 back into the profit function: P(4) = -2(4)^2 + 16(4) - 24 = -32 + 64 - 24 = 8. Therefore, the maximum profit Tasty Bites can achieve from selling Chicken Crunch sandwiches, while adhering to the constraints, is $8."}	9
MCQ-Single	<Pure Contextual> - <Arithmetic> - <Critical Reasoning> - <Ratio and Proportion> - <difficulty_level: 1>	740	3	2	Determining the Number of Fruit Shops in a Quirky Town	In a quirky town, there are two types of shops: fruit shops and vegetable shops. For every 3 fruit shops, there are 2 vegetable shops. If there are a total of 50 shops in the town, how many fruit shops are there? You need to determine the number of fruit shops based on the given ratio.	1	0	0	{}	2025-02-08 05:07:53.913	2025-02-08 05:07:53.913	f	\N	39	t	{"solution": "To find the number of fruit shops, we start by noting the given ratio of fruit shops to vegetable shops, which is 3:2. To determine the total number of parts represented in the ratio, we add the parts together: 3 (fruit) + 2 (vegetable) = 5 parts in total. Since the total number of shops in the town is 50, we can find the proportion of fruit shops by calculating (3/5) * 50. Therefore, the number of fruit shops is 30."}	10
MCQ-Single	<Pure Contextual> - <Algebra> - <Backsolving> - <Functions> - <difficulty_level: 1>	478	3	2	Finding the Total Cost of Lattes at a Quirky Café	A quirky café is known for serving unique flavored lattes. The café offers three sizes of lattes - small, medium, and large. If the price of a small latte is represented by \\( x \\), the medium latte costs \\( 1.5x \\), and the large latte costs \\( 2.2x \\). If a customer orders one small, one medium, and one large latte, what is the total cost in terms of \\( x \\)?	1	0	0	{}	2025-02-07 05:21:30.484	2025-02-07 05:21:30.484	f	\N	32	t	{"solution": "To find the total cost of the lattes in terms of \\\\( x \\\\), we can calculate as follows:<br><br>1. The cost of a small latte is \\\\( x \\\\).<br>2. The cost of a medium latte is \\\\( 1.5x \\\\).<br>3. The cost of a large latte is \\\\( 2.2x \\\\).<br><br>Now, the total cost can be expressed as:<br>\\\\[ \\\\text{Total Cost} = x + 1.5x + 2.2x \\\\]<br>\\\\[ \\\\text{Total Cost} = (1 + 1.5 + 2.2)x \\\\]<br>\\\\[ \\\\text{Total Cost} = 4.7x \\\\]<br><br>Thus, the total cost of one small, one medium, and one large latte is \\\\( 4.7x \\\\)."}	6
MCQ-Single	<Real Contextual> - <Word Problems> - <Setting up proper steps(questions that require users to properly setting up the steps to solve the questions)> - <Inequalities> - <Accounting> - <difficulty_level: 1>	479	3	2	Inequalities in Profit Management: An Accounting Dilemma	In a small accounting firm, Sarah is tasked with managing the financial records for two different clients, Client A and Client B. Client A's records are expected to generate a profit of at least \\$1,500, while Client B's records should yield a profit of at least \\$1,200. If Sarah's total profit from both clients cannot exceed \\$3,000 due to budget constraints set by her firm, which of the following inequalities represents the situation described? Let x represent the profit from Client A and y represent the profit from Client B.	1	0	0	{}	2025-02-07 05:21:30.516	2025-02-07 05:21:30.516	f	\N	32	t	{"solution": "The situation can be represented by the following inequalities:<ul><li>\\\\( x \\\\geq 1500 \\\\) - Profit from Client A</li><li>\\\\( y \\\\geq 1200 \\\\) - Profit from Client B</li><li>\\\\( x + y \\\\leq 3000 \\\\) - Total profit constraint</li></ul>These inequalities reflect the requirements of profit generation set for Sarah in the accounting firm."}	7
MCQ-Single	<Real Contextual> - <Word Problems> - <Mathematical tools(Questions which may have 2 or more mathematical approachs to solve, but user would have to choose the most optimal and efficient approach: generate question content in that manner)> - <Polynomials> - <Strategy and Management> - <difficulty_level: 4>	480	3	2	Optimizing Resource Allocation for Project Efficiency in Strategic Management	In a recent evaluation of a strategic management initiative aimed at enhancing project efficiency, a company's project manager devised a polynomial model representing the relationship between the number of resources allocated (x) and the completion time (y) in days for a specific project. The polynomial is defined as y = 3x^2 - 12x + 18, where x must be a positive integer. The management wants to assess the completion time as resources are adjusted, noting that they aim for a completion time no greater than 30 days. Considering the constraints involved in resource allocation, the project manager sets aside a budget allowing for the deployment of up to 8 resources. However, they also receive feedback from team members suggesting that employing a reduction strategy by redistributing existing resources could optimize completion time without exceeding the set budget. Based on this, what is the maximum number of resources that can be allocated while still ensuring the project is completed in accordance with the stipulated timeframe of 30 days?	4	0	0	{}	2025-02-07 05:21:30.55	2025-02-07 05:21:30.55	f	\N	32	t	{"solution": "<p>To solve the problem, we start by setting the polynomial equal to 30, since we want to find when the project can be completed in at most 30 days:</p> <p>~~y = 3x^{2} - 12x + 18 = 30~~</p> <p>Rearranging gives:</p> <p>~~3x^{2} - 12x + 18 - 30 = 0~~</p> <p>Which simplifies to:</p> <p>~~3x^{2} - 12x - 12 = 0~~</p> <p>Now, we can factor or use the quadratic formula:</p> <p>Using the quadratic formula: ~~x = \\\\frac{-b \\\\pm \\\\sqrt{b^{2} - 4ac}}{2a}~~</p> <p>Where:\\n - a = 3\\n - b = -12\\n - c = -12</p> <p>Calculating the discriminant:</p> <p>~~b^{2} - 4ac = (-12)^{2} - 4(3)(-12) = 144 + 144 = 288~~</p> <p>Now applying the quadratic formula:</p> <p>~~x = \\\\frac{12 \\\\pm \\\\sqrt{288}}{6}~~</p> <p>This gives two possible solutions. However, since we are interested in positive integer values of x, we only consider those solutions which are greater than zero. Solving further:</p> <p>After calculating, the relevant solution for x that aligns with the conditions of resource allocation is approximately: ~~x \\\\approx 4.83~~</p> <p>Since x must be a positive integer, we take the maximum possible integer value, thus:</p> <p>The maximum number of resources that can be allocated while ensuring project completion within 30 days is: <strong>5</strong>.</p>"}	8
MCQ-Single	<Pure Contextual> - <Algebra> - <Number Picking(by logical and critical reasoning over constraints given in the question)> - <Polynomials> - <difficulty_level: 5>	481	3	2	Polynomial Evaluation in a Competitive Scenario	In a mathematical competition, participants were tasked with solving a complex polynomial equation defined as -5x^2 + -8x + 5y + -2. The evaluators noticed that the first variable, x, is greatly affected by the value of y. To streamline the grading, it was determined that when x is set to 5, the total value of the polynomial must yield a sum close to -40. Only the candidates who can critically evaluate the function and correctly deduce the other values will pass. Which of the following values of y would allow the polynomial to satisfy the condition stated by the evaluators?	5	0	0	{}	2025-02-07 05:21:30.584	2025-02-07 05:21:30.584	f	\N	32	t	{"solution": "<p>To determine the value of y that satisfies the polynomial equation, we start with the given values:</p> <p>Let \\\\( x = 5 \\\\) and we want the polynomial to sum up to \\\\( -40 \\\\).</p> <p>Substituting \\\\( x \\\\) into the polynomial:</p> <p>\\\\( -5x^{2} + -8x + 5y + -2 = -40 \\\\)</p> <p>This simplifies to:</p> <p>\\\\( -5(5)^{2} + -8(5) + 5y + -2 = -40 \\\\)</p> <p>Calculating the left-hand side:</p> <p>\\\\( -5(25) + -40 + 5y - 2 = -40 \\\\)</p> <p>Which simplifies to:</p> <p>\\\\( -125 + 5y - 2 = -40 \\\\)</p> <p>Now, combining the constants:</p> <p>\\\\( 5y - 127 = -40 \\\\)</p> <p>Adding 127 to both sides gives:</p> <p>\\\\( 5y = 87 \\\\)</p> <p>Dividing both sides by 5 yields:</p> <p>\\\\( y = \\\\frac{87}{5} = 17.4 \\\\)</p><p>Thus, the value of y that would allow the polynomial to satisfy the evaluators' condition is:</p> <p>\\\\( y = 17.4 \\\\)</p>"}	9
MCQ-Single	<Real Contextual> - <Arithmetic> - <Critical Reasoning> - <Unitary Method> - <difficulty_level: 1>	482	3	2	Flour Calculation for Bread Production in a Bakery	In a small bakery, the baker uses 2 kg of flour to make 16 loaves of bread. If she wants to make 48 loaves, how much flour does she need to use? A helpful tip: think about how much flour is used for each loaf and then scale it accordingly.	1	0	0	{}	2025-02-07 05:21:30.615	2025-02-07 05:21:30.615	f	\N	32	t	{"solution": "To determine the amount of flour required for 48 loaves, we first find out how much flour is used for one loaf.<br><br>1. Calculate flour per loaf:<br>   \\\\text{Flour per loaf} = \\\\frac{2 \\\\text{ kg}}{16 \\\\text{ loaves}} = 0.125 \\\\text{ kg per loaf}<br><br>2. Now, to find the flour needed for 48 loaves:<br>   \\\\text{Total flour for 48 loaves} = 0.125 \\\\text{ kg/loaf} \\\\times 48 \\\\text{ loaves} = 6.0 \\\\text{ kg}<br><br>Thus, the total amount of flour required to produce 48 loaves of bread is 6.0 kg."}	10
MCQ-Single	<Pure Contextual> - <Algebra> - <Number Picking(by logical and critical reasoning over constraints given in the question)> - <Polynomials> - <difficulty_level: 2>	483	3	2	Maximizing Flowers Planted in a Community Garden Using a Polynomial Model	A local gardening club has decided to plant a new type of flower in their community garden. They have created a polynomial equation to model the number of flowers (f) they can plant based on the number of garden beds (b). The equation is given by f(b) = -1b^3 + 4b^2 + 1b + -4. The club currently has 4 garden beds available for planting. If they want to maximize the number of flowers planted while still staying within the positive integer quantity of flowers, what is the maximum number of flowers they can plant using their polynomial equation? Choose the appropriate number of garden beds they should use from the options provided.	2	0	0	{}	2025-02-07 05:21:30.651	2025-02-07 05:21:30.651	f	\N	32	t	{"solution": "<h3>Solution:</h3> <p>To find the maximum number of flowers that can be planted using the polynomial equation <strong>f(b) = -1b^3 + 4b^2 + 1b - 4</strong>, we evaluate this polynomial for the integer values of garden beds (b) from 1 to 4:</p> <ul> <li>For b = 1: f(1) = -1(1^3) + 4(1^2) + 1(1) - 4 = 0</li> <li>For b = 2: f(2) = -1(2^3) + 4(2^2) + 1(2) - 4 = 6</li> <li>For b = 3: f(3) = -1(3^3) + 4(3^2) + 1(3) - 4 = 8</li> <li>For b = 4: f(4) = -1(4^3) + 4(4^2) + 1(4) - 4 = 0</li> </ul> <p>Thus, the maximum number of flowers that can be planted using 3 garden beds is <strong>8</strong>.</p>"}	11
MCQ-Single	<Pure Contextual> - <Word Problems> - <Setting up proper steps(questions that require users to properly setting up the steps to solve the questions)> - <Trial and Error Method(type of questions)> - <Marketing and Sales> - <difficulty_level: 1>	741	3	2	Calculating the Sale Price and Revenue from a Promotional Cookie Sale	In a small town, a local bakery decides to run a promotional sale to increase customer engagement. The bakery sets the price of a dozen cookies at $18. If they plan to offer a 10% discount on the cookies for a week, calculate the sale price of a dozen cookies during the promotion. Additionally, if the bakery aims to sell 50 dozen cookies during this promotional week, how much revenue will they generate from these sales at the discounted price? Please show your calculations clearly.	1	0	0	{}	2025-02-08 05:07:53.948	2025-02-08 05:07:53.948	f	\N	39	t	{"solution": "To find the sale price after applying the discount, we first need to calculate the amount of the discount. The original price of a dozen cookies is $18. We calculate the discount amount as follows: \\\\n\\\\n1. Discount Amount = Original Price × Discount Percentage = $18 × 0.10 = $1.80. \\\\n\\\\nNow, we subtract the discount amount from the original price to find the sale price: \\\\n\\\\n2. Sale Price = Original Price - Discount Amount = $18 - $1.80 = $16.20. \\\\n\\\\nNext, we calculate the total revenue generated from the sale of 50 dozens at this sale price. We use the following formula: \\\\n\\\\n3. Total Revenue = Sale Price × Number of Dozens = $16.20 × 50 = $810. \\\\n\\\\nThus, the sale price of a dozen cookies during the promotion will be $16.20, generating a total revenue of $810."}	11
MCQ-Single	<Real Contextual> - <Algebra> - <Number Picking(by logical and critical reasoning over constraints given in the question)> - <Polynomials> - <difficulty_level: 3>	742	3	2	Finding the Price of Cakes Through Polynomial Equations in a Bakery Promotion	In a small town, the local bakery sells three types of cakes: chocolate, vanilla, and red velvet. The price of a chocolate cake, 'x', is represented by the polynomial 2x^2 + 3x - 5. The cost of vanilla cakes is represented by the polynomial x^2 - 4x + 4, and the price of red velvet cakes is described by the polynomial 3x^2 + x - 2. The bakery has set a promotion where customers can buy a chocolate cake and a vanilla cake for a total of $10. If the cost of a red velvet cake is equal to the sum of the costs of chocolate and vanilla cakes, what would be the value of 'x' if the price of a red velvet cake must also satisfy the equation |cost of chocolate + cost of vanilla| = cost of red velvet?	3	0	0	{}	2025-02-08 05:07:53.983	2025-02-08 05:07:53.983	f	\N	39	t	{"solution": "To solve the problem, we must first analyze the costs of the cakes represented by the given polynomials:\\n\\n1. Chocolate cake cost: 2x² + 3x - 5.\\n2. Vanilla cake cost: x² - 4x + 4.\\n3. Red velvet cake cost: 3x² + x - 2.\\n\\nGiven that the total cost for a chocolate cake and a vanilla cake is $10, we can establish the equation:\\n\\n(2x² + 3x - 5) + (x² - 4x + 4) = 10.\\n\\nSimplifying this gives:\\n3x² - x - 1 = 0.\\n\\nUsing the quadratic formula, the possible solutions for x are:\\nx = 1/6 - sqrt(133)/6 and x = 1/6 + sqrt(133)/6.\\n\\nNext, we must satisfy the condition that the price of a red velvet cake equals the sum of the costs of the other two cakes:\\n\\nSet up the equation:\\n\\n2x² + 3x - 5 + x² - 4x + 4 = 3x² + x - 2.\\n\\nThis simplifies to:\\n3x² - x - 1 = 0.\\n\\nFrom this, the correct solution simplifies to:\\nx = 1/2. \\n\\nThus, the value of x that satisfies the conditions set by the problem is 1/2."}	12
MCQ-Single	<Pure Contextual> - <Arithmetic> - <common pitfalls> - <Discount, Profit and Loss> - <difficulty_level: 1>	743	3	2	Calculating the Final Price After Discount on a Handcrafted Vase	In a quaint village, a local artisan offers a stunning handcrafted vase for a price of $60. However, during a weekend market event, she decides to give a 10% discount on the vase to attract more customers. If a shopper visits the market, how much will the shopper pay for the vase after applying the discount?	1	0	0	{}	2025-02-08 05:07:54.017	2025-02-08 05:07:54.017	f	\N	39	t	{"solution": "To determine the final price of the vase after applying the discount, we first need to calculate the amount of the discount. The discount percentage is given as 10%. Therefore, the discount amount can be calculated as follows: Discount Amount = (Discount Percentage / 100) * Original Price. Plugging in the values, we get Discount Amount = (10 / 100) * 60 = 6. Next, we subtract the discount amount from the original price to find the final price. Final Price = Original Price - Discount Amount = 60 - 6 = 54. Hence, the shopper will pay $54 for the vase."}	13
MCQ-Single	<Real Contextual> - <Word Problems> - <Assessing given Situation(checking the ability of accessing a given situation)> - <Unitary Method> - <Logistics and Supply Chain> - <difficulty_level: 3>	744	3	2	Optimizing Delivery Trips in a Logistics Company	In a bustling logistics and supply chain company, a manager is faced with the task of transporting goods from the warehouse to multiple retail locations. The manager has a truck that can carry a maximum of 500 kilograms at a time. Each retail location requires a specific amount of goods to be delivered: Store A needs 150 kilograms, Store B requires 220 kilograms, and Store C requires 140 kilograms. If the manager's goal is to minimize the number of trips made while ensuring that each store receives its required amount, what is the optimal delivery arrangement? Assume the manager can combine the deliveries to two stores in one trip, but Store C must be visited separately due to its location constraints. How many total trips will the manager have to make to fulfill all the deliveries under these constraints?	3	0	0	{}	2025-02-08 05:07:54.051	2025-02-08 05:07:54.051	f	\N	39	t	{"solution": "To determine the optimal delivery arrangement for the manager, we first assess the total goods needed by each store. Store A requires 150 kilograms, Store B requires 220 kilograms, and Store C requires 140 kilograms. The truck can carry a maximum of 500 kilograms at once. \\n\\nWe can combine the deliveries for Store A and Store B since their combined total of 370 kilograms (150 + 220) is less than the truck's capacity. Therefore, we can make one trip for both Store A and Store B. Meanwhile, Store C needs a separate trip because of its location constraint. \\n\\nIn total, the manager will need 1 trip for the deliveries to Store A and Store B combined and 1 additional trip for Store C. Thus, the total number of trips the manager has to make to fulfill all the deliveries will be 2."}	14
TC-1	<Politics> - <TC-1> - <difficulty-level: 1> - <vocabulary-level:1>	801	2	1	Political Parties in Modern Democracies	In modern democracies, the role of political parties is to __________ the differing views of the populace, ensuring that a diverse range of opinions is considered in the governance process.	1	0	0	{}	2025-02-08 05:11:43.07	2025-02-08 05:11:43.07	f	\N	44	t	{"solution": "<p><strong>C</strong> is the correct option because political parties actively seek to <em>embrace</em> the differing views of the populace, fostering inclusivity in government decisions.</p> <p>Other options are not suitable for the following reasons:</p> <ul> <li><strong>A</strong> - While parties aim to clarify views, this does not encompass the idea of inclusion.</li> <li><strong>B</strong> - Assessing views does not imply representation or action.</li> <li><strong>D</strong> - Undermining views contradicts the purpose of political parties in a democracy.</li> <li><strong>E</strong> - Disregarding differing views would lead to a narrow governance approach.</li> <li><strong>F</strong> - Marginalizing voices undermines the democratic fabric.</li> </ul>"}	2
MCQ-Single	<Pure Contextual> - <Word Problems> - <Setting up proper steps(questions that require users to properly setting up the steps to solve the questions)> - <Algebraic Equations> - <Accounting> - <difficulty_level: 2>	745	3	2	Calculating Total Revenue and Profit for QuirkyQuills in a Promotional Month	In a quirky accounting scenario, a fictional company called QuirkyQuills specializes in creating intricate feather pens. Last month, they sold a total of 450 pens at a price of $12 each. During a special promotion, they decided to offer a 20% discount on the pens sold after the threshold of 300 pens was crossed. This promotion turned out to be a hit, leading to an additional 50 pens being sold at the discounted price. In addition to these sales, the company had fixed costs of $1,800 for the month. Given this information, determine the total revenue generated from pen sales and calculate whether QuirkyQuills managed to cover their fixed costs. What steps would you take to arrive at the total profit or loss for QuirkyQuills for the given month?	2	0	0	{}	2025-02-08 05:07:54.085	2025-02-08 05:07:54.085	f	\N	39	t	{"solution": "To determine the total revenue generated by QuirkyQuills from pen sales and whether they covered their fixed costs, we can break down the solution into several clear steps:\\n\\n1. First, calculate the revenue generated from the first 300 pens sold at the regular price: 300 pens x $12 = $3,600.\\n\\n2. Next, identify how many pens were sold at the discounted price. Since a total of 450 pens were sold and the discount applied to the pens sold beyond 300, that means 150 pens were sold at the discount.\\n\\n3. Calculate the discounted price of each pen, which is 20% off the regular price. The discounted price is thus $12 - ($12 x 0.20) = $12 - $2.40 = $9.60.\\n\\n4. Now, calculate the revenue generated from these 150 discounted pens: 150 pens x $9.60 = $1,440.\\n\\n5. Add the revenue from regular sales and discounted sales to find the total revenue: $3,600 + $1,440 = $5,040.\\n\\n6. Finally, determine the total profit or loss. Subtract the fixed costs of $1,800 from the total revenue: $5,040 - $1,800 = $3,240.\\n\\nIn conclusion, QuirkyQuills generated a total revenue of $5,040 and a profit of $3,240 after covering their fixed costs."}	15
MCQ-Single	<Pure Contextual> - <Word Problems> - <Choosing correct mathematical tools to solve problems(Questions which may have 2 or more mathematical approachs to solve, but user would have to choose the most optimal and efficient approach: generate question content in that manner)> - <Functions> - <Resource Management> - <difficulty_level: 1>	746	3	2	Resource Allocation for Environmental Project	In a small community, a committee is planning a resource allocation for a local environmental project that spans several months. They have a total budget of $10,000 to be divided among three distinct activities: tree planting, waste management, and community education workshops. The committee has decided to allocate 50% of the budget to tree planting, 30% to waste management, and the remainder to community education. How much money is allocated to each activity?	1	0	0	{}	2025-02-08 05:07:54.127	2025-02-08 05:07:54.127	f	\N	39	t	{"solution": "To solve the problem, we start by identifying the total budget allocated for the environmental project, which is $10,000. The problem specifies the budget allocation percentages for each activity. First, we calculate the allocation for tree planting: 50% of $10,000 equals $5,000. Next, for waste management, we calculate 30% of $10,000, resulting in $3,000. Finally, we determine the remainder for community education workshops. Since the total percentage allocated for tree planting and waste management is 80% (50% + 30%), the remaining percentage is 20%. Therefore, the community education budget is 20% of the total budget, which is $2,000. In summary: Tree planting receives $5,000, waste management receives $3,000, and community education workshops receive $2,000."}	16
MCQ-Single	<Real Contextual> - <Algebra> - <Backsolving> - <Polynomials> - <difficulty_level: 2>	747	3	2	Calculating the Cost of Producing Gadgets Using Polynomial Functions	A small company specializes in creating custom-made gadgets, and they have a specific design which is a polynomial function. The total cost, \\( C(x) \\), of producing \\( x \\) gadgets is represented by the polynomial \\( C(x) = 3x^3 - 5x^2 + 2x + 10 \\). If the company wants to find out the cost of producing 4 gadgets, which corresponds to the value of \\( x \\), they need to identify the output of their cost function for this specific input. However, they suspect that the costs could be slashed if they produce more items, so they also wish to evaluate the cost when producing 5 and 6 gadgets. By comparing the resultant costs, they hope to decide whether increasing production makes financial sense. How much will it cost to produce these three different quantities of gadgets?	2	0	0	{}	2025-02-08 05:07:54.158	2025-02-08 05:07:54.158	f	\N	39	t	{"solution": "To calculate the cost of producing gadgets based on the polynomial function \\\\( C(x) = 3x^3 - 5x^2 + 2x + 10 \\\\), we will evaluate the function at three different values of \\\\( x \\\\): 4, 5, and 6. \\\\n\\\\n1. First, we evaluate \\\\( C(4) \\\\): \\\\n   \\\\( C(4) = 3(4)^3 - 5(4)^2 + 2(4) + 10 \\\\) \\\\n   \\\\( = 3(64) - 5(16) + 8 + 10 \\\\) \\\\n   \\\\( = 192 - 80 + 8 + 10 = 130 \\\\). \\\\n\\\\n2. Next, we evaluate \\\\( C(5) \\\\): \\\\n   \\\\( C(5) = 3(5)^3 - 5(5)^2 + 2(5) + 10 \\\\) \\\\n   \\\\( = 3(125) - 5(25) + 10 + 10 \\\\) \\\\n   \\\\( = 375 - 125 + 10 + 10 = 270 \\\\). \\\\n\\\\n3. Finally, we evaluate \\\\( C(6) \\\\): \\\\n   \\\\( C(6) = 3(6)^3 - 5(6)^2 + 2(6) + 10 \\\\) \\\\n   \\\\( = 3(216) - 5(36) + 12 + 10 \\\\) \\\\n   \\\\( = 648 - 180 + 12 + 10 = 490 \\\\). \\\\n\\\\nThus, the costs for producing 4, 5, and 6 gadgets are \\\\( 130 \\\\), \\\\( 270 \\\\), and \\\\( 490 \\\\) respectively."}	17
MCQ-Single	<Pure Contextual> - <Algebra> - <Backsolving> - <Polynomials> - <difficulty_level: 3>	748	3	2	Finding Integer Solutions of a Polynomial in an Art Gallery Scenario	In a quirky art gallery, the owner decides to display sculptures that are represented by the polynomial P(x) = 3x² - 5x + 2. To promote their art, they want to organize an exhibition with various sculptures, but they've set a condition. For a chosen sculpture, the polynomial must equal zero at the certain points. If the artist claims that the sculptures can be displayed if they satisfy P(x) = 0, what are the possible x-values that can actually result in the visualization of the art? As the owner knows that two sculptures can be displayed at the same spot, he asks whether the x-values that satisfy this equation include integer values. Knowing this, he also wants to explore which of the potential integer solution options among x = 1, 2, and 3 produces the correct display of sculptures. Using this scenario, determine the integer solutions for P(x) = 0 and decide which of the given x-values are valid solutions for displaying the beautiful sculptures.	3	0	0	{}	2025-02-08 05:07:54.197	2025-02-08 05:07:54.197	f	\N	39	t	{"solution": "To solve the polynomial P(x) = 3x² - 5x + 2 for its roots, we can use the quadratic formula or factorization. The roots can be found using the equation ax² + bx + c = 0, where a = 3, b = -5, and c = 2. The solutions for this polynomial are obtained as follows: \\n\\n1. Apply the quadratic formula: x = [ -b ± √(b² - 4ac) ] / (2a). \\n2. Calculate the discriminant: b² - 4ac = (-5)² - 4*(3)*(2) = 25 - 24 = 1. \\n3. Therefore, x = [ 5 ± √(1) ] / (2*3) = [ 5 ± 1 ] / 6. \\n4. This results in two potential solutions: x = (5 + 1) / 6 = 1 and x = (5 - 1) / 6 = 2/3. \\n5. The integer solution obtained is x = 1. Thus, the integer x-value that can result in the visualization of the sculptures is 1."}	18
MCQ-Single	<Real Contextual> - <Arithmetic> - <common pitfalls> - <Rates> - <difficulty_level: 2>	749	3	2	Total Package Delivery Calculation for Bicycle Couriers	In a bustling city, a bicycle courier can deliver packages at a rate of 12 packages per hour. Due to rising demand, the courier company decides to hire an additional part-time courier. The new courier is capable of delivering packages at 18 packages per hour but only works for 2 hours a day. If both couriers work together for one day (8 hours), how many total packages will they deliver in that day? Keep in mind that the first courier works the entire 8 hours while the new courier works only for 2 hours.	2	0	0	{}	2025-02-08 05:07:54.232	2025-02-08 05:07:54.232	f	\N	39	t	{"solution": "To find the total packages delivered by both couriers, we first calculate the delivery of each courier separately. The first courier delivers packages at a rate of 12 packages per hour over 8 hours, so the total for the first courier is 12 * 8 = 96 packages. The new part-time courier delivers 18 packages per hour but only works for 2 hours, thus delivering 18 * 2 = 36 packages in that time. Adding both couriers' deliveries together gives us a total of 96 + 36 = 132 packages delivered in one day."}	19
MCQ-Single	<Real Contextual> - <Arithmetic> - <Number Sense> - <Trial and Error Method(type of questions)> - <difficulty_level: 1>	750	3	2	Maximum Cakes Production at the Local Fair	A bakery produces a variety of cakes and sells them at a local fair. Each cake requires 3 eggs, 250 grams of flour, and 150 grams of sugar. If the bakery has a total of 12 eggs, 1,000 grams of flour, and 600 grams of sugar available for the fair, what is the maximum number of whole cakes the bakery can produce without exceeding the available ingredients?	1	0	0	{}	2025-02-08 05:07:54.265	2025-02-08 05:07:54.265	f	\N	39	t	{"solution": "To determine the maximum number of whole cakes the bakery can produce, we evaluate the available ingredients in relation to the requirements for each cake. Each cake requires 3 eggs, 250 grams of flour, and 150 grams of sugar. Given the total ingredients, we perform the following calculations:\\n\\n1. Calculate maximum cakes based on eggs:\\n   - Total eggs available: 12\\n   - Eggs required per cake: 3\\n   - Maximum cakes by eggs = Total eggs / Eggs per cake = 12 / 3 = 4.\\n\\n2. Calculate maximum cakes based on flour:\\n   - Total flour available: 1000 grams\\n   - Flour required per cake: 250 grams\\n   - Maximum cakes by flour = Total flour / Flour per cake = 1000 / 250 = 4.\\n\\n3. Calculate maximum cakes based on sugar:\\n   - Total sugar available: 600 grams\\n   - Sugar required per cake: 150 grams\\n   - Maximum cakes by sugar = Total sugar / Sugar per cake = 600 / 150 = 4.\\n\\n4. The overall maximum number of cakes produced will be the minimum of the maximums determined from each ingredient, which is: \\n   Minimum (4, 4, 4) = 4.\\n\\nHence, the bakery can produce a maximum of 4 whole cakes."}	20
MCQ-Single	<Real Contextual> - <Algebra> - <Number Picking(by logical and critical reasoning over constraints given in the question)> - <Polynomials> - <difficulty_level: 5>	751	3	2	Determining Area Allocations in an Urban Development Project	In a bustling metropolis, a new urban development project is underway, aimed at creating a new state-of-the-art shopping complex. The complex's total area is a polynomial represented by P(x) = 4x^3 - 3x^2 + 12x - 27, where x is the number of square meters allocated per section. The developers also have an exclusive contract with local artisans, requiring at least 3 different sections of the complex to be allocated to unique artisan shops, while the remaining sections can be utilized for other retail spaces. In addition, the project must conform to zoning regulations stating that, at minimum, the total square footage allocated to artisan shops must equal 15% of the total area. However, each artisan shop can only occupy areas that are polynomial functions of their section, specifically, A(x) = 2x^2 - x + 5. As the lead urban planner, your goal is to determine how many square meters can effectively be allocated to non-artisan retail sections while satisfying all given constraints. If the project plans to divide the total area evenly among the artisan shops and the remaining sections, and considering all dotted zoning regulations, how many square meters can you allocate to the remaining sections without violating any restrictions? Consider all polynomial representations in your calculations and ensure that the final allocation adheres to both the zoning laws and the physical limitations of the plot.	5	0	0	{}	2025-02-08 05:07:54.302	2025-02-08 05:07:54.302	f	\N	39	t	{"solution": "To determine the allocation for non-artisan retail sections, we have the total area of the complex represented by the polynomial P(x) = 4x^3 - 3x^2 + 12x - 27. The zoning regulations require that at least 15% of this total area is allocated to artisan shops. Each artisan shop occupies an area given by the polynomial A(x) = 2x^2 - x + 5. Given that we must allocate space to 3 artisan shops, the total area allocated to artisan shops becomes 3 * A(x). Thus, we set up the equation: 3 * A(x) = 0.15 * P(x). Solving this yields the polynomial equation that relates x to the total area allocations.\\n\\nEvaluating various possible values for x (the square meters per section), we find:\\n- For x = 1, Total Area = -14, therefore negative allocation is not feasible.\\n- For x = 2, Total Area = 17, artisan area = 33; non-artisan area = 17 - 33 = -16 (impossible).\\n- For x = 3, Total Area = 90, artisan area = 60; non-artisan area = 90 - 60 = 30.\\n- For x = 4, Total Area = 229, artisan area = 99; non-artisan area = 229 - 99 = 130.\\n\\nThus, valid allocations for non-artisan retail sections are derived at x = 3 and x = 4, yielding 30 and 130 square meters respectively. The highest feasible allocation is 130 square meters."}	21
CR	<psychology> - <CR> - <find the assumption> - <difficulty_level: 2>	752	4	2	Identifying the Assumption in Social Connections and Mental Health Argument	What is the assumption in the statement that 'fostering social ties may lead to better mental health outcomes'?	2	0	0	{"passages": ["Recent studies in psychology have indicated that people who frequently engage in creative activities tend to report higher levels of overall happiness than those who do not. This suggests that participating in creative endeavors not only promotes mental engagement but could also serve as a vital component of emotional well-being. Therefore, encouraging individuals to pursue creative hobbies may significantly enhance their quality of life.", "According to research in psychology, social interactions are crucial for mental health. Individuals who maintain strong social connections report lower levels of stress and a reduced risk of depression. This relationship implies that fostering social ties may lead to better mental health outcomes. Consequently, communities should prioritize activities that promote social engagement among their members."]}	2025-02-08 05:07:54.343	2025-02-08 05:07:54.343	f	\N	40	t	{"solution": "The correct answer is <b>A</b>: Stronger social connections correlate with lower stress levels.<br> This choice directly supports the assumption that fostering social ties can lead to better mental health outcomes. <br><o>Option <b>B</b>: Social engagements are the only method to improve mental health is incorrect because the argument does not claim that social engagements are the sole solution; it suggests they are crucial.</o> <br><o>Option <b>C</b>: Mental health is influenced solely by external factors is incorrect because the argument implies that social connections are a significant factor, not the only one.</o> <br><o>Option <b>D</b>: Individuals with better mental health prefer fewer social interactions contradicts the premise, as it suggests the opposite of the argument's conclusion about social connections.</o> <br><o>Option <b>E</b>: Communities can benefit from enhancing social engagement activities is a conclusion rather than an assumption and does not address the link between social ties and mental health.</o>"}	1
CR	<biological_sciences> - <CR> - <structure of the argument boldface structure question> - <difficulty_level: 4>	753	4	2	Identify roles of bolded statements in oceanic fish population argument	In the argument presented, identify the roles of the following statements: <b>1) Recent analysis of oceanic data has indicated that overfishing is not the primary cause of declines in fish populations.</b> <b>2) It has been suggested that environmental changes, such as temperature shifts and ocean acidification, have substantial impacts.</b>	4	0	0	{"passages": ["Recent studies suggest that the rapid decline of bee populations is largely attributed to the prevalence of certain pesticides. Proponents of this theory argue that these chemicals disrupt the bees' navigational abilities, leading to decreased foraging success and ultimately declining hive numbers. However, some researchers contend that factors such as habitat loss and climate change also play significant roles in this phenomenon. Thus, both sides present compelling arguments, yet the link between pesticide use and bee decline remains a subject of intense debate.", "A recent analysis of oceanic data has indicated that overfishing is not the primary cause of declines in fish populations as previously thought. Instead, it has been suggested that environmental changes, such as temperature shifts and ocean acidification, have substantial impacts. The researchers who argue this point highlight that fish stocks have shown resilience in areas with sustainable fishing practices but are still declining in regions facing severe environmental changes. This distinction raises critical questions about current fisheries management policies, particularly concerning the effectiveness of regulating fishing quotas without addressing environmental factors."]}	2025-02-08 05:07:54.367	2025-02-08 05:07:54.367	f	\N	40	t	{"solution": "The correct answer is D: Both statements are supporting premises that explain different aspects of fish population decline.<br> <o> The first statement establishes that overfishing is not the primary cause of fish population declines, while the second statement introduces environmental changes as significant factors. Together, they provide a comprehensive understanding of the issue at hand.<br> <o> A is incorrect because neither statement serves as a conclusion. Both are premises that contribute to the argument's rationale.<br> <o> B is incorrect because the first statement is not a conclusion; it is an assertion that requires further support.<br> <o> C is incorrect because while the first statement presents a fact, it is not an assumption; it directly informs the discussion.<br> <o> E is incorrect because neither statement functions as an assumption; both are presented as findings of the analysis."}	2
CR	<psychology> - <CR> - <strengthen the argument> - <difficulty_level: 5>	754	4	2	Strengthening the Argument on Sleep and Cognitive Function	Which of the following, if true, would most strengthen the argument that consistent sleep schedules enhance cognitive function?	5	0	0	{"passages": ["Recent studies in psychology have shown that individuals who engage in regular physical exercise demonstrate significantly higher levels of mental well-being compared to those who do not. This suggests that physical activity is not only beneficial for physical health but also plays a crucial role in enhancing psychological health. For instance, a survey conducted across various demographics revealed that participants who exercised at least three times a week reported lower stress levels and improved mood. However, some critics argue that external factors, such as social support and nutrition, could also contribute to these findings. Nonetheless, the evidence strongly indicates that incorporating exercise into daily routines can be a pivotal strategy for improving both mental and physical health. To further bolster this argument, additional research could be conducted to investigate the direct relationship between exercise frequency and specific psychological outcomes.", "The correlation between sleep quality and cognitive function has been well-documented in psychological literature. Numerous studies indicate that individuals who achieve a consistent sleep schedule exhibit enhanced attention, memory retention, and problem-solving abilities. For example, a longitudinal study demonstrated that participants with improved sleep hygiene significantly outperformed their counterparts on cognitive tasks that required high levels of concentration. While critics argue that cognitive function can also be influenced by factors like stress and learning opportunities, it is clear that prioritizing sleep can significantly improve cognitive performance. To strengthen this argument, it would be beneficial to explore research that isolates sleep as the primary variable affecting cognitive outcomes among different populations, thereby ruling out external influences."]}	2025-02-08 05:07:54.385	2025-02-08 05:07:54.385	f	\N	40	t	{"solution": "The best option that strengthens the argument is option D: 'Athletes who adhered to strict sleep schedules demonstrated improved reaction times and decision-making.' This provides direct evidence that maintaining a consistent sleep schedule can lead to better cognitive outcomes, specifically in areas directly related to cognitive function. <br> <o> <b>Option A:</b> This option mentions a correlation between lack of sleep and memory issues, but it does not provide evidence of improved cognitive function from consistent sleep schedules. <br> <o> <b>Option B:</b> Although this supports the idea that consistent sleep leads to feeling more alert, it does not directly link this feeling to enhanced cognitive abilities or performance on cognitive tasks. <br> <o> <b>Option C:</b> While it highlights an external factor (stress) affecting sleep and cognition, it does not strengthen the argument about the benefits of consistent sleep schedules in enhancing cognitive function. <br> <o> <b>Option E:</b> This adds information about diet impacting cognitive function, which could introduce an alternative explanation, thus weakening the argument advocating for sleep as the main factor."}	3
CR	<biological_sciences> - <CR> - <draw inference/conclusion> - <difficulty_level: 2>	755	4	2	Inference about Evolutionary Traits of Resilient Plants	Based on the passage, what can be inferred about the evolutionary traits of plants that thrive in harsh conditions?	2	0	0	{"passages": ["Recent studies in biological sciences suggest that exposure to diverse environments enhances the adaptability of certain species. For instance, a population of birds raised in varying conditions showed increased foraging efficiency compared to those raised in controlled environments. This adaptability likely stems from the exposure to different stimuli that stimulate problem-solving skills in these birds. Consequently, species that inhabit changing environments might possess greater resilience to climate shifts and other ecological threats.", "In the realm of biological sciences, it has been observed that certain plants exhibit a remarkable ability to thrive in harsh conditions. Research has indicated that these plants often develop deeper root systems and thicker leaves, which provide both water and nutrient retention advantages. Furthermore, studies have shown that these adaptations allow them to outcompete less resilient plant species in arid environments. Therefore, it can be inferred that the evolutionary traits of such plants are crucial for their survival in challenging climates."]}	2025-02-08 05:07:54.403	2025-02-08 05:07:54.403	f	\N	40	t	{"solution": "The correct answer is A: <br>These plants are likely to have developed adaptations that enhance their survival chances in diverse environments. This inference directly relates to the passage that discusses how certain plants thrive due to specific evolutionary traits. <br><o>Option B is incorrect because the passage does not state that these plants require less water; instead, it emphasizes their abilities to retain water more effectively.</o> <br><o>Option C is not supported by the passage, which focuses on survival traits rather than reproduction rates.</o> <br><o>Option D is incorrect since the passage suggests that resilient plants can outcompete others in harsh environments, not that they cannot compete.</o> <br><o>Option E is misleading because the adaptations mentioned are beneficial in challenging climates, not limited to dry climates alone.</o>"}	4
CR	<philosophy> - <CR> - <structure of the argument boldface structure question> - <difficulty_level: 2>	756	4	2	Identify the roles of boldface statements in Thompson's art argument	In the argument by Mark Thompson, the two boldface statements serve different roles. What is the role of the first boldface statement: 'art must derive from genuine emotion to be considered valuable,' and the second boldface statement: 'some might argue that technical skill alone can create art of significant value'? <br> <b>Identify the functions of both statements in the context of the argument.</b>	2	0	0	{"passages": ["In a recent article, the renowned philosopher Sarah Dillon argues that ethical behavior is fundamental to personal happiness. She claims that individuals who consistently act in accordance with their moral beliefs foster positive relationships and create a supportive community. Furthermore, Dillon asserts that a lack of ethical behavior leads to personal dissatisfaction and societal discord. However, she acknowledges that some may counter that happiness can be achieved through selfish pursuits, regardless of moral considerations. In addressing this counterargument, Dillon emphasizes that true happiness is not merely the absence of suffering but is instead rooted in meaningful connections with others.", "The philosopher Mark Thompson presents a view in which he boldly states that art must derive from genuine emotion to be considered valuable. He posits that art lacking authentic emotional grounding fails to resonate with its audience, thus rendering it less impactful. However, he also boldly admits that some might argue that technical skill alone can create art of significant value, independent of emotional connection. In response to this viewpoint, Thompson insists that emotional authenticity is what ultimately drives the appreciation of art, turning mere technical production into something truly profound."]}	2025-02-08 05:07:54.422	2025-02-08 05:07:54.422	f	\N	40	t	{"solution": "The correct answer is E: The first statement is a premise; the second is a counter to the premise.<br> <o>In the argument, Thompson asserts that genuine emotion is essential for art to have value, making this his main premise.</o> <br> <o>The second boldface statement introduces an opposing viewpoint, arguing that technical skill can create valuable art independently of emotion, thus acting as a counter to Thompson's premise.</o> <br> <o>Option A is incorrect because the first boldface statement is not a conclusion; it serves as a foundational premise.</o> <br> <o>Option B is incorrect because the first statement is not a general assumption but rather a strong assertion supporting the value of art.</o> <br> <o>Option C is incorrect as the first statement is a premise and not a conclusion, while the second is not a conclusion but rather an opposing argument.</o> <br> <o>Option D is incorrect because the first statement does not serve as a counterargument, but rather as the primary claim that the second statement challenges.</o>"}	5
CR	<social_sciences> - <CR> - <structure of the argument dialogue structure question> - <difficulty_level: 1>	757	4	2	Analyzing Mr. Lee's Argument in the Environmental Policy Discussion	In the discussion between Ms. Johnson and Mr. Lee, what role does Mr. Lee's argument about the potential costs to businesses play in the overall dialogue regarding stricter carbon emission regulations?	1	0	0	{"passages": ["In a recent discussion between two economists, Dr. Green argued that increasing the minimum wage would reduce poverty levels. He emphasized that with higher wages, employees would have more disposable income to spend on necessities, which in turn would boost local economies. Dr. White countered this viewpoint by stating that raising the minimum wage might lead to businesses hiring fewer employees, as increased labor costs could lead to higher unemployment rates. Dr. Green responded by arguing that the potential increase in wages would likely lead to better productivity and lower employee turnover, benefiting businesses in the long run. The economists ended their discussion without reaching a consensus, each maintaining their stance on the implications of increasing the minimum wage.", "During a panel discussion on environmental policies, Ms. Johnson asserted that implementing stricter regulations on carbon emissions would significantly decrease air pollution. She stated that countries with strict emissions standards have witnessed marked improvements in air quality. Mr. Lee challenged this assertion by suggesting that such regulations could potentially lead to increased costs for businesses, which might turn to cheaper, less environmentally friendly practices in other countries. Ms. Johnson replied by highlighting that the long-term health benefits and reduced healthcare costs would outweigh the short-term economic challenges. The panel concluded their conversation without finding common ground, with both sides firmly believing in their perspectives on environmental regulation."]}	2025-02-08 05:07:54.439	2025-02-08 05:07:54.439	f	\N	40	t	{"solution": "The correct answer is <b>C</b>: Mr. Lee's argument acts as a counterpoint to Ms. Johnson's claim about the benefits of stricter regulations.<br> <o>This response correctly identifies Mr. Lee's role in the dialogue, where he challenges Ms. Johnson's assertion by presenting a potential negative outcome associated with stricter regulations.</o><br> <o><b>A</b> is incorrect because Mr. Lee's argument does not support the idea that stricter regulations could harm economic growth; rather, it questions the impact of these regulations.</o><br> <o><b>B</b> is wrong since Mr. Lee's argument does not assume that costs will always increase; he argues that they might increase, which is not the same.</o><br> <o><b>D</b> is incorrect because Mr. Lee's response does not derive from Ms. Johnson's evidence but challenges it.</o><br> <o><b>E</b> is misleading; Mr. Lee does not suggest that regulations are unnecessary based on air quality but rather expresses a concern about economic consequences.</o>"}	6
CR	<culture> - <CR> - <paradox> - <difficulty_level: 2>	758	4	2	Exploring the Paradox of Cultural Greetings and Behaviors	What does the passage illustrate about the nature of cultural behaviors, particularly in relation to the act of greeting? <br> The passage highlights the paradox of differing cultural practices, emphasizing how a behavior can embody both positive and negative connotations, depending on the societal context.	2	0	0	{"passages": ["In many cultures, the act of greeting is steeped in traditions that reflect the values of that society. For instance, in some cultures, a warm handshake accompanies a friendly greeting, signaling openness and trust. Contrarily, in certain Eastern cultures, a bow is preferred, representing respect and humility. This discrepancy raises an interesting paradox: How can two seemingly opposite forms of greeting both represent positive social interactions? Both greetings convey an essential human need for connection and acknowledgment, regardless of the cultural style employed.", "Cultural practices often highlight a fascinating paradox where behaviors that are deemed polite in one context may be considered rude in another. For example, maintaining eye contact during conversation is viewed as a sign of confidence in Western cultures. However, in some Asian cultures, too much eye contact might be interpreted as confrontational or disrespectful. This leads to the question: How can a behavior embody both respect and disrespect across different cultures? Understanding this paradox can deepen our appreciation for the complexity of social interactions worldwide."]}	2025-02-08 05:07:54.461	2025-02-08 05:07:54.461	f	\N	40	t	{"solution": "The correct answer is A: Cultural greetings reflect underlying social values and can vary widely between societies.<br> This option accurately captures the essence of the passage, which discusses how different cultures have distinct practices, such as handshakes and bows, that signify social values.<br><o>Option B is incorrect because it generalizes that all cultures agree on the importance of eye contact and physical greetings, which the passage contradicts.</o><br><o>Option C is incorrect as it suggests that respect is shown through the same gestures across cultures, ignoring the diversity highlighted in the passage.</o><br><o>Option D is incorrect because the passage implies that greeting behaviors are significant in social interactions, contrasting the idea that they have little impact.</o><br><o>Lastly, Option E is incorrect since the passage emphasizes the importance of understanding cultural differences for meaningful social interactions.</o>"}	7
CR	<literature> - <CR> - <structure of the argument boldface structure question> - <difficulty_level: 3>	759	4	2	Identifying the Role of a Statement in an Argument	In the passage, the author comments that `the protagonist in the play is a young artist who struggles to find her voice in a patriarchal society`. What role does this statement serve in the overall argument?	3	0	0	{"passages": ["In her recent novel, the author presents a series of characters who grapple with their identities in a rapidly changing society. While some characters embrace transformation, others resist it, leading to varied outcomes. The author argues that self-acceptance can be a powerful catalyst for personal growth, often challenging societal norms. Therefore, the author's exploration of identity serves not only to entertain but also to provoke thought on the complexities of human experience.", "The protagonist in the play is a young artist who struggles to find her voice in a patriarchal society. The playwright asserts that her artistic journey mirrors the broader feminist movement, highlighting the obstacles women face in the art world. As the protagonist confronts societal expectations, she ultimately discovers her unique style. This journey reflects the larger theme that breaking free from societal constraints can lead to both personal and artistic liberation."]}	2025-02-08 05:07:54.482	2025-02-08 05:07:54.482	f	\N	40	t	{"solution": "The correct answer is A: <br> 'Premise supporting the artist's struggles against societal norms' - This statement serves as a premise in the argument, illustrating the challenges the protagonist faces, which is essential for understanding the broader themes the author explores. <br> <o> B: 'Conclusion about the impact of patriarchal society on female artists' - This is incorrect because the statement is a premise, not a conclusion. <br> <o> C: 'Assumption that the protagonist is representative of all female artists' - This option is misleading, as the statement does not make a universal claim about all female artists but focuses on the protagonist. <br> <o> D: 'Counterargument to the notion that women are successfully breaking barriers' - This is incorrect as the statement does not counter any argument; it presents a situation faced by the protagonist. <br> <o> E: 'Evidence of the protagonist's eventual success in a male-dominated field' - This is incorrect because the statement focuses on the struggle, not on her success."}	8
CR	<culture> - <CR> - <structure of the argument boldface structure question> - <difficulty_level: 3>	760	4	2	Identifying Argument Structure in Street Art Discussion	In the argument above, the statement 'Proponents argue that it transforms bleak public spaces into vibrant communities, encouraging social interaction and appreciation for art' serves which of the following roles in the author's argument?	3	0	0	{"passages": ["The recent trend in culinary innovation emphasizes the importance of local sourcing and seasonal ingredients. Many chefs argue that utilizing local produce not only supports regional economies but also enhances the flavors of their dishes. However, some culinary critics contend that this focus on locality can limit creativity and result in less diverse menus. They assert that by confining their ingredients to what is locally available, chefs may inadvertently restrict their culinary artistry. Thus, while local sourcing may be beneficial in certain aspects, there is a risk that it stifles innovation in the culinary field.", "In urban environments, street art has gained recognition as a legitimate form of artistic expression. Proponents argue that it transforms bleak public spaces into vibrant communities, encouraging social interaction and appreciation for art. They believe that street art can reflect the culture and identity of a city, serving as a historical record of the time. However, critics caution that unsanctioned street art can lead to vandalism and urban decay, detracting from the perceived value of legitimate art forms. Therefore, while street art may contribute positively to urban aesthetics, there is an ongoing debate regarding its implications for community standards and artistic legitimacy."]}	2025-02-08 05:07:54.499	2025-02-08 05:07:54.499	f	\N	40	t	{"solution": "The correct answer is <strong>B</strong>: It serves as a supporting premise for the argument in favor of street art.<br> This statement supports the idea that street art has positive effects on communities, which is in line with the proponents' views discussed in the passage.<br><br> <strong>A</strong>: This option is incorrect because the statement does not present a counterargument; it reinforces the proponents' stance.<br> <strong>C</strong>: This option is incorrect as the statement does not serve as a conclusion but rather as evidence supporting the main argument.<br> <strong>D</strong>: This option is incorrect because the statement does not introduce concerns about legitimacy; it advocates for the benefits of street art.<br> <strong>E</strong>: This option is incorrect because the statement does not highlight negative effects; instead, it emphasizes the positive contributions of street art."}	9
TC-3	<Literature> - <TC-3> - <difficulty-level: 4> - <vocabulary-level:1>	802	2	1	Literature: Protagonist's Values and Human Nature	In the realm of literature, the protagonist often embodies the values of _______ and _______ that are central to the novel’s overarching themes, while simultaneously illustrating the complexities of human nature through _______ behavior.	4	0	0	{}	2025-02-08 05:11:43.097	2025-02-08 05:11:43.097	f	\N	44	t	{"solution": "<p>The correct answers are <b>compassion</b>, <b>altruistic</b>, and <b>exemplary</b> as these words collectively represent the values that a protagonist in literature typically embodies. Together, they illustrate a character who is not only caring and selfless but also serves as a model for others.</p><p><u>Explanation of other options:</u></p><ul><li><b>sacrilege</b>: This term refers to violation of something sacred, which is contrary to the positive values expected of a protagonist.</li><li><b>indifference</b>: This word implies a lack of concern or interest, contrary to compassionate behavior.</li><li><b>nostalgic</b>: While it may reflect a yearning for the past, it does not tie strongly to altruism or compassion.</li><li><b>heroic</b>: Although it suggests bravery, it doesn't necessarily align with the values of compassion.</li><li><b>malevolent</b>: This denotes a desire to harm others, which is the opposite of the expected qualities in a protagonist.</li><li><b>irresponsible</b>: This implies a lack of accountability, which contradicts the exemplary nature of a protagonist.</li><li><b>exuberant</b>: While it denotes enthusiasm, it does not reflect the serious values embodied by a protagonist.</li><li><b>apologetic</b>: This indicates remorse, which does not align with the proactive qualities of a character who embodies strong values.</li></ul>"}	3
SE	<Politics> - <SE> - <difficulty-level: 1> - <vocabulary-level:2>	803	2	1	Political Campaign Communication	The recent campaign was notable not only for its innovative approach to voter outreach but also for the candidates' ability to communicate their visions in a manner that was both _______ and _______.	1	0	0	{}	2025-02-08 05:11:43.14	2025-02-08 05:11:43.14	f	\N	44	t	{"solution": "<p>The correct options are <b>candid</b> and <b>articulate</b> because both words imply clarity and honesty in communication, traits essential for effective political discourse.</p><p>Other options are less suitable because:</p><ul><li><b>Confusing</b>: implies lack of clarity.</li><li><b>Ambiguous</b>: suggests unclear messaging.</li><li><b>Incomprehensible</b>: indicates it cannot be understood.</li><li><b>Transparent</b>: while positive, it does not fit as well in the context of communication style alongside the first blank.</li></ul>"}	4
TC-3	<Psychology> - <TC-3> - <difficulty-level: 2> - <vocabulary-level:2>	804	2	1	Cognitive Dissonance and Its Psychological Impacts	In psychology, the concept of cognitive dissonance refers to the mental discomfort experienced when an individual holds two or more conflicting beliefs or values. This dissonance can lead to a variety of outcomes, including changes in attitudes, __________ responses to information, and a heightened need for __________ validation. Ultimately, individuals strive for __________ in their beliefs, as the tension created by dissonance can be psychologically taxing.	2	0	0	{}	2025-02-08 05:11:43.169	2025-02-08 05:11:43.169	f	\N	44	t	{"solution": "<p><strong>A</strong>: The term 'emotional' fits well in the context of 'responses to information,' as cognitive dissonance often triggers emotional reactions. <br> <strong>F</strong>: 'External' validation is relevant, as individuals seek outside confirmation to alleviate dissonance. <br> <strong>I</strong>: 'Consistency' ties with the goal of aligning beliefs to resolve the discomfort of dissonance.</p> <p>Other options do not fit as effectively: <br> <strong>B</strong> ('physical') and <strong>C</strong> ('observable') do not relate to psychological responses; <br> <strong>D</strong> ('inauthentic'), <strong>E</strong> ('social'), <strong>G</strong> ('self-referential'), <strong>H</strong> ('identical'), <strong>J</strong> ('discrepancy'), <strong>K</strong> ('ambiguity'), and <strong>L</strong> ('disharmony') do not adequately capture the psychological striving for balance and resolution.</p>"}	5
TC-2	<Philosophy> - <TC-2> - <difficulty-level: 2> - <vocabulary-level:3>	805	2	1	Philosophical Reflection and Principles	Many philosophers contend that the essence of ethical behavior is not merely adherence to prescribed norms, but rather a deeper understanding of being, requiring individuals to engage in _______ reflection on their principles and to _______ those principles in the context of human experience.	2	0	0	{}	2025-02-08 05:11:43.216	2025-02-08 05:11:43.216	f	\N	44	t	{"solution": "<p><b>Option B</b> (critical) is correct because it indicates a deep, thoughtful examination of ethical principles, which aligns with engaging in meaningful reflection. <br> <br> <b>Option F</b> (reassess) is also correct since it implies evaluating and possibly altering one's principles based on reflection.  <br> <br> <b>Option A</b> (superficial) suggests a lack of depth in reflection, making it incorrect. <br> <br> <b>Option C</b> (ambiguous) does not fit as it would not suggest a clear understanding of ethical behavior. <br> <br> <b>Option D</b> (unquestioning) contradicts the notion of engagement in critical thinking. <br> <br> <b>Option E</b> (articulate) does not fit as it relates to expression rather than reflection and engagement. <br> <br> <b>Option G</b> (ignore) and <b>Option H</b> (disregard) both imply neglect and do not align with the idea of thoughtful ethical engagement.</p>"}	6
MCQ-Single	<Real Contextual> - <Word Problems> - <Obtaining the best answer(which has confusing options, luring the user to choose the wrong one)> - <Percentages> - <Business> - <difficulty_level: 2>	815	3	2	Calculating the Effective Final Payment After A Discount at a Coffee Shop	In a bustling city, a coffee shop is known for its specialty brews and exquisite blends. The owner decided to run a promotional offer that claims customers will receive a 20% discount on their total bill for every purchase exceeding $50. Last Saturday, the shop was buzzing with customers who jumped at this opportunity. A customer named Sarah bought two bags of premium coffee beans priced at $30 each and a bottle of limited-edition syrup priced at $25. To make the most of the discount, she also included an extra cupcake priced at $5. As her total before any discount was calculated, an unexpected dilemma arose: Should she use the discount on her entire purchase, or was it more beneficial to forego the cupcake? Calculate the amount she needs to pay after applying the discount on her purchase, and consider the possible outcomes of removing the cupcake from her total. What is the final amount Sarah would need to pay if she chooses to include the cupcake in her purchase?	2	0	0	{}	2025-02-09 03:33:00.821	2025-02-09 03:33:00.821	f	\N	45	t	{"solution": "To determine the final amount Sarah needs to pay, we start by calculating her total purchases. She bought 2 bags of coffee at $30 each, a bottle of syrup for $25, and a cupcake for $5. Therefore, the total cost is calculated as follows: \\\\n\\\\nTotal cost = (2 * $30) + $25 + $5 = $60 + $25 + $5 = $90.  \\\\n\\\\nSince her total purchase exceeds $50, Sarah is eligible for a 20% discount on her total bill. The discount amount is given by: \\\\nDiscount = 20% of $90 = 0.20 * $90 = $18. \\\\n\\\\nThus, the final amount she needs to pay after applying the discount is: \\\\nFinal amount = Total cost - Discount = $90 - $18 = $72. \\\\n\\\\nIf she opts to exclude the cupcake from her purchase, her new total would be: \\\\nNew total cost = (2 * $30) + $25 = $60 + $25 = $85. \\\\n\\\\nAgain, since this amount exceeds $50, she would still get a 20% discount on the new total: \\\\nDiscount without cupcake = 20% of $85 = 0.20 * $85 = $17. \\\\n\\\\nHence, the final amount without the cupcake would be: \\\\nFinal amount without cupcake = New total cost - Discount without cupcake = $85 - $17 = $68. \\\\n\\\\nIn summary, including the cupcake results in a final payment of $72, whereas excluding it results in a total of $68."}	1
CR	<philosophy> - <CR> - <evaluate the conclusion> - <difficulty_level: 1>	500	4	2	Evaluating Conclusions on Moral Relativism in Ethical Debates	Based on the passage, which of the following conclusions can be accurately drawn regarding moral relativism and its implications for ethical debates?	1	0	0	{"passages": ["Philosophers often argue about the nature of truth and its relationship to reality. Some contend that truth is an objective characteristic, independent of human perception, while others believe that truth is subjective, shaped by cultural and individual contexts. A recent debate highlighted this divide, with proponents of objective truth arguing that scientific discoveries reveal universal truths about the world, while advocates for subjective truth claim that different perspectives can lead to equally valid interpretations of realities. Ultimately, the discussion poses critical questions about how we evaluate the conclusions we draw from our experiences and observations.", "In philosophy, the concept of moral relativism suggests that moral judgments are not absolute but rather shaped by cultural, societal, and personal influences. Proponents argue that what is considered right or wrong can vary from one society to another, and as such, no single moral framework should be viewed as superior. This position raises important considerations for ethical debates, as it challenges the validity of universal moral principles. Critics, however, argue that this view can lead to a dangerous tolerance of harmful practices, suggesting a need for some overarching moral standards. Thus, the ongoing discourse about moral relativism and its implications invites us to critically evaluate the conclusions drawn about ethics in a diverse world."]}	2025-02-07 05:21:31.123	2025-02-07 05:21:31.123	f	\N	33	t	{"solution": "The correct answer is C: Critics of moral relativism argue for the necessity of universal moral standards to prevent harm.<br><o>This option accurately reflects the passage's discussion about how critics of moral relativism see the potential dangers of a lack of absolute ethical guidelines.</o><br><o>Option A is incorrect because it misrepresents moral relativism; while it recognizes different moral perspectives, it does not claim they are all equally valid without context.</o><br><o>Option B is also incorrect as it suggests that proponents of moral relativism advocate for a singular dominant perspective, which contradicts their fundamental belief in the multiplicity of moral views.</o><br><o>Option D is misleading since moral relativism recognizes that ethical practices may differ across cultures, implying that practices can evolve over time.</o><br><o>Lastly, option E is incorrect because the debate on moral relativism is highly relevant to contemporary ethical discussions, as evidenced by ongoing ethical dilemmas in diverse societies.</o>"}	5
CR	<philosophy> - <CR> - <find the assumption> - <difficulty_level: 2>	501	4	2	Identify the assumption in deontological ethics regarding moral actions	What assumption is made by the proponent of deontological ethics in the argument presented regarding moral actions and their consequences?	2	0	0	{"passages": ["The philosophical notion of utilitarianism posits that the best action is one that maximizes utility, typically defined as that which produces the greatest well-being of the greatest number of people. Some critics argue that this approach fails to take into account the long-term consequences of actions, focusing instead on immediate outcomes. However, proponents claim that by prioritizing overall happiness, utilitarianism leads to more ethical decision-making. Therefore, they argue that when faced with a moral dilemma, one should always opt for the course of action that benefits the majority.", "In examining moral philosophies, one often encounters deontological ethics, which assert that the morality of an action is based on whether that action itself is fundamentally right or wrong, regardless of the consequences. This view is contrasted with consequentialist theories, which judge actions based on their outcomes. A common assumption underlying deontological perspectives is that there are inherent moral rights and duties that do not depend on the potential results of an action. Thus, when making ethical decisions, it is crucial to recognize these moral imperatives."]}	2025-02-07 05:21:31.14	2025-02-07 05:21:31.14	f	\N	33	t	{"solution": "<o>The correct answer is B: 'There are actions that are inherently right or wrong regardless of outcomes.' This statement captures the core assumption of deontological ethics, which posits that moral actions are judged based on their own intrinsic nature rather than their consequences.</o><br><o>Option A is incorrect because it contradicts the foundational principle of deontology, which emphasizes that moral rights and duties exist independently of consequences.</o><br><o>Option C is incorrect as it references a consequentialist perspective rather than a deontological one, which does not prioritize outcomes in moral decision-making.</o><br><o>Option D is incorrect because it advocates for consequentialism, which deontological ethics explicitly stands against.</o><br><o>Option E is incorrect as it conflates deontological ethics with a perspective that prioritizes individual happiness over collective good, which is not a tenet of deontology.</o>"}	6
CR	<culture> - <CR> - <paradox> - <difficulty_level: 1>	502	4	2	Understanding the Paradox of Cultural Identity and Transformation	What is the paradox presented in the passage concerning cultural identity and its transformation?	1	0	0	{"passages": ["In many societies, cultural practices are often seen as rigid and unchanging. However, historical evidence suggests that cultures are not static; they evolve over time in response to various factors such as globalization, technological advancements, and social movements. This presents a paradox: while many individuals may strongly identify with and cling to their cultural traditions, these very traditions may be changing or disappearing as society progresses. Hence, the question arises: how can a culture be both a source of identity and a subject to transformation?", "Cultural identity is often perceived as a fixed and uniform characteristic that individuals possess. Yet, the reality is often contradictory. On one hand, people take pride in their heritage and maintain traditions that have been passed down through generations. On the other hand, exposure to different cultures through travel, migration, or technology frequently leads individuals to adopt new practices and beliefs that may dilute their original cultural identities. This raises a paradox: how can one claim to uphold their cultural heritage while simultaneously embracing influences from other cultures?"]}	2025-02-07 05:21:31.156	2025-02-07 05:21:31.156	f	\N	33	t	{"solution": "The correct answer is B: <br> Cultural practices evolve in response to external influences while still being embraced by individuals. This option reflects the paradox described in the passage, where individuals maintain a sense of cultural identity even as they adapt to new influences. <br> <o> Option A is incorrect because it ignores the dynamic nature of cultural identity that the passage discusses. <br> <o> Option C is incorrect as it suggests that outside influences must be completely rejected, contradicting the concept of cultural evolution presented in the passage. <br> <o> Option D is incorrect because the passage implies that cultural transformation has been ongoing throughout history, not just a recent phenomenon. <br> <o> Option E is also incorrect because it fails to recognize that cultural identity can, and often does, incorporate change and adapt over time."}	7
CR	<history> - <CR> - <complete the argument> - <difficulty_level: 1>	503	4	2	Completion of the Argument on the Renaissance's Impact	Based on the passage, which of the following best completes the argument: 'Thus, the Renaissance not only revived classical knowledge but also ________.'	1	0	0	{"passages": ["The ancient Greeks made significant contributions to the fields of art, science, and philosophy, which have continued to influence modern civilization. For instance, their development of democratic principles laid the foundation for contemporary political systems. Furthermore, their innovative approaches in mathematics and geometry, such as the Pythagorean theorem, have shaped the way we understand the world today. Therefore, one can argue that without the contributions of the ancient Greeks, our understanding of democracy, art, and science would be markedly different.", "During the Renaissance period, a revival of interest in classical knowledge began to spread across Europe. This movement not only led to advancements in art and architecture but also spurred significant progress in science and technology. For example, Leonardo da Vinci's studies of anatomy improved our understanding of the human body, while Galileo's innovations in astronomy changed how we perceive our place in the universe. Therefore, it can be concluded that the Renaissance was a pivotal time that not only celebrated the achievements of ancient civilizations but also laid the groundwork for modern scientific inquiry."]}	2025-02-07 05:21:31.173	2025-02-07 05:21:31.173	f	\N	33	t	{"solution": "The correct answer is A: 'initiated a new era of artistic expression and scientific exploration.' This option logically follows the passage's argument that the Renaissance built upon classical knowledge and contributed significantly to advancements in various fields.<br> <o>Option B is incorrect because the passage highlights significant progress in philosophical thought during the Renaissance.</o> <br> <o>Option C is incorrect as the passage clearly states the profound impact of the Renaissance on modern society.</o> <br> <o>Option D is inaccurate because the passage discusses broader achievements beyond just the revival of Greek art.</o> <br> <o>Option E is also incorrect since the passage emphasizes advancements in technology and science rather than restrictions.</o>"}	8
CR	<history> - <CR> - <strengthen the argument> - <difficulty_level: 1>	504	4	2	Strengthening the Argument for the Printing Press's Role in the Renaissance	Which of the following, if true, would most strengthen the argument that the printing press was instrumental in shaping the transformative nature of the Renaissance?	1	0	0	{"passages": ["Throughout history, many civilizations have thrived primarily due to their innovations in agricultural practices. For instance, the ancient Mesopotamians developed irrigation systems that allowed them to control water flow, which in turn significantly boosted their crop yields. This advancement in agriculture helped sustain larger populations and facilitated trade. Consequently, it is clear that agricultural innovation is not merely a supportive element but a critical factor in the success and expansion of civilizations.", "The Renaissance, a period of significant cultural and intellectual revival in Europe, was largely fueled by the increased availability of printed materials. The invention of the printing press allowed for the rapid dissemination of ideas, particularly those related to science and philosophy. This surge in accessible knowledge not only inspired advancements in various fields but also empowered individuals to challenge traditional beliefs. Therefore, it can be posited that the printing press was instrumental in shaping the transformative nature of the Renaissance."]}	2025-02-07 05:21:31.191	2025-02-07 05:21:31.191	f	\N	33	t	{"solution": "The correct answer is C. This statement directly supports the argument by indicating that classical texts, which were vital to the intellectual advancements of the Renaissance, became widely accessible because of the printing press. <br> <o> Option A, while true, only discusses the limitations of handwritten manuscripts without connecting it to the transformative nature of the Renaissance. <br> <o> Option B discusses a decline in religious influence but does not directly relate to how the printing press contributed to broader knowledge dissemination. <br> <o> Option D highlights economic prosperity but does not specifically address the role of the printing press. <br> <o> Option E contradicts the argument that the printing press was instrumental in shaping the Renaissance by suggesting it was only used for religious texts, thereby weakening the overall argument."}	9
		505	4	2	Implications of Physical Sciences in Technological Advancements	What can be inferred about the practical significance of thermodynamics, quantum mechanics, and electromagnetism in modern technology based on the passages?	-1	0	0	{}	2025-02-07 05:21:31.214	2025-02-07 05:21:31.214	t	51	33	t	{"solution": "<p>The correct answer is <strong>A</strong>: These scientific principles are essential for the development of innovative technologies, such as renewable energy and quantum computing.</p><p>This option accurately reflects the implications drawn from the passages, which discuss how thermodynamics, quantum mechanics, and electromagnetism are not only foundational theories but also crucial for advancing technology.</p><p><strong>B</strong>: The principles of physical sciences have no significant impact on contemporary technological applications. <em>This statement is incorrect as the passages highlight the direct applications of these scientific principles in various technologies.</em></p><p><strong>C</strong>: Understanding these concepts is primarily important for academic purposes and does not influence real-world technology. <em>The passages clearly indicate that these principles are vital for practical applications, thus this option is also incorrect.</em></p><p><strong>D</strong>: Scientific advances in physics are solely confined to theoretical frameworks and do not translate into practical applications. <em>This statement contradicts the essence of the passages, which emphasize the significant real-world applications of physical sciences.</em></p>"}	10
DS	<permutations and combinations>- <difficulty-level: 3>	761	1	1	Unique Arrangements of Fruit Salad in a Culinary Contest	Is the information provided in the statements sufficient to determine the total number of unique arrangements of the fruit salad the chef can prepare?	3	0	0	{"passage": "In a culinary contest featuring various dessert recipes, a chef has 5 different types of fruits and wishes to create a fruit salad using 3 of them. The order in which the fruits are combined matters for presentation. Furthermore, the chef considers that using the same fruit more than once is prohibited. How many unique arrangements of the fruit salad can the chef prepare?", "statements": ["The chef selects 3 different fruits from the 5 available fruits.", "The arrangement of the fruits in the salad is allowed to change based on presentation preferences."]}	2025-02-08 05:11:42.013	2025-02-08 05:11:42.013	f	\N	41	t	{"solution": "To determine the total number of unique arrangements of the fruit salad, we need to consider both statements provided. Statement (1) tells us that the chef selects 3 different fruits from a total of 5 fruits, which gives us a combination of fruits. The number of ways to choose 3 fruits from 5 can be calculated using the combination formula: \\\\(\\\\binom{5}{3} = 10\\\\). Statement (2) informs us that the arrangement of these fruits is important. For each selection of 3 fruits, there are \\\\(3! = 6\\\\) different ways to arrange them. Hence, the total unique arrangements the chef can prepare is calculated as \\\\(10 \\\\times 6 = 60\\\\). Both statements together provide the necessary information to answer the question."}	1
DS	<geometry>- <difficulty-level: 2>	762	1	1	Comparing Volumes of a Cylinder with Modified Height	Is the new volume of the cylinder twice the original volume based on the given information?	2	0	0	{"passage": "A cylindrical container has a radius of r and a height of h. The volume V of the cylinder can be calculated using the formula V = πr^2h. If the height of the cylinder is doubled and the radius remains the same, what is the new volume of the cylinder compared to the original?", "statements": ["The original volume of the cylinder is 50π cubic units.", "The height of the cylinder is 10 units."]}	2025-02-08 05:11:42.062	2025-02-08 05:11:42.062	f	\N	41	t	{"solution": "From Statement (1), we know the original volume is 50π cubic units. From Statement (2), the height is 10 units. Therefore, the original radius can be calculated using the volume formula: 50π = πr^2(10), which simplifies to r^2 = 5, thus r = √5. When the height is doubled to 20 units, the new volume becomes V = π(√5)^2(20) = 100π cubic units, which is indeed double the original volume (50π). Therefore, both statements together provide enough information to affirm that the new volume is double the original. Overall, we conclude that EITHER statement ALONE is not sufficient, meaning the correct answer is C."}	2
DS	<number theorm>- <difficulty-level: 1>	763	1	1	Representations of the Number 10 as Sum of Prime Numbers	Is it true that there are exactly three representations for the number 10 as the sum of two primes based on the above statements?	1	0	0	{"passage": "In a certain number system, every even number is expressed as the sum of two prime numbers. For example, the number 6 can be represented as 3 + 3 or 5 + 1. Are there exactly three representations for the number 10 using the mentioned rule?", "statements": ["Statement (1): The prime numbers less than 10 are 2, 3, 5, and 7. Statement (2): There are four different pairs of prime numbers whose sum equals 10."]}	2025-02-08 05:11:42.104	2025-02-08 05:11:42.104	f	\N	41	t	{"solution": "To determine if there are exactly three representations of the number 10 as the sum of two primes, we can analyze the statements. From Statement (1), we know the primes less than 10 are 2, 3, 5, and 7. We can form the pairs (3, 7), (5, 5), and (2, 8), but since 8 is not prime, it is excluded. From Statement (2), we identify the pairs (3, 7), (5, 5), and the repeated pair (2, 8) which we exclude. Hence, there are only two valid pairs, not three, consistent with the conclusion that Statement (1) is insufficient alone. Statement (2) proposes four pairs, which contradicts the total valid pairs found from (1). Therefore, the correct option is E, as no combination suffices to confirm the claim made in (1) or (2)."}	3
NE	<speed, distance and time>- <difficulty-level: 1>	764	1	1	The Mythical Race of the Minotaur and Centaur	In a peculiar race of mythical creatures, a speedy Minotaur runs at a constant speed of 12 meters per second for the first 5 seconds. Shortly thereafter, a mischievous Centaur joins the race and runs at a speed of 15 meters per second. If both creatures continue running at their respective speeds, what will be the total distance covered by both the Minotaur and the Centaur after 10 seconds of the race?	1	0	0	{"answer": 135.0}	2025-02-08 05:11:42.146	2025-02-08 05:11:42.146	f	\N	41	t	{"solution": "<p>Distance covered by Minotaur in first 5 seconds = ~~12 m/s * 5 s = 60 m~~ <br> Distance covered by Centaur in the remaining 5 seconds = ~~15 m/s * 5 s = 75 m~~ <br> Total distance covered by both = ~~60 m + 75 m = 135 m~~ </p>"}	4
DS	<number theorm>- <difficulty-level: 1>	765	1	1	Prime Number Game in a Village Festival	Based on the above passage, can we determine if the sum of the coins held by villagers A and B will satisfy the prime requirement for the next festival?	1	0	0	{"passage": "In a small village, the residents have organized a festival where villagers are challenged to participate in a unique number game. Each villager has a certain number of coins, which is a prime number less than 50. It is known that the sum of the coins held by two villagers, A and B, is also a prime number. Additionally, no villager holds more than 30 coins. The village has a specific rule that the sum of the coins of any two villagers must remain a prime number for the next festival to be possible. Understanding these rules could aid in predicting the possible combinations of coins villagers could have in the future.", "statements": ["The number of coins held by villager A is 17.", "The number of coins held by villager B is 19."]}	2025-02-08 05:11:42.156	2025-02-08 05:11:42.156	f	\N	41	t	{"solution": "To determine if the sum of the coins held by villagers A and B is prime, we calculate the sum: 17 + 19 = 36. However, 36 is not a prime number (as it can be divided by 2, 3, and others). Therefore, we can conclude that the information given in the statements is sufficient to answer the question about whether the sum satisfies the prime requirement for the next festival, which it does not. Hence, the correct answer is option A, as statement 1 alone provides sufficient information to answer the question."}	5
MCQ-Multi	<profit, loss and discount>- <difficulty-level: 1> (multi-correct MCQ)	766	1	1	Savings and Profits in a Handmade Vase Sale	In a small town, a curious shopkeeper decided to run a special sale event for the local community. The shopkeeper set a regular price of $200 for a unique handcrafted vase. For the sale, the shopkeeper intended to offer a discount of 25% off the regular price. Additionally, the shopkeeper had previously set a markup of 20% on the original wholesale cost of $150. If a customer purchases two vases during the sale, what are the total savings from the discount and the effective profit per vase based on the original wholesale cost?	1	0	0	{}	2025-02-08 05:11:42.197	2025-02-08 05:11:42.197	f	\N	41	t	{"solution": "<p>Regular Price of Vase: $200 <br> Discount Percentage: 25% <br> Discount Amount: ~~200 * 25% = 50~~ <br> Discounted Price: ~~200 - 50 = 150~~ <br> Total Savings for Two Vases: ~~50 * 2 = 100~~ <br> Wholesale Cost of Vase: $150 <br> Markup Percentage: 20% <br> Markup Amount: ~~150 * 20% = 30~~ <br> Selling Price After Markup: ~~150 + 30 = 180~~ <br> Effective Profit Per Vase: ~~150 - 180 = -30 (Loss)~~ </p>"}	6
MCQ-Single	<fractions/decimals and Unitary method>- <difficulty-level: 1>	767	1	1	Determining the Number of Daisies per Bouquet in a Wizard's Enchanted Garden	In a mystical garden filled with enchanted flowers, a wizard collects 24 magical daisies. Each day, he carefully arranges these daisies into bouquets. On the first day, he creates 6 bouquets, and each bouquet contains an equal number of daisies. On the second day, he picks 12 more daisies, and he decides to create twice as many bouquets as the previous day using all the daisies he now has. How many daisies did he place in each bouquet on the second day?	1	0	0	{}	2025-02-08 05:11:42.223	2025-02-08 05:11:42.223	f	\N	41	t	{"solution": "<p>On the first day, the wizard creates 6 bouquets.<br> Therefore, each bouquet contains 4.0 daisies. <br> On the second day, he picks 12 additional daisies, making it a total of 36 daisies.<br> Now, he decides to create 12 bouquets, thus each bouquet on the second day contains 3.0 daisies.</p>"}	7
MCQ-Multi	<Unitary method>- <difficulty-level: 3> (multi-correct MCQ)	768	1	1	Calculating the Total Chores for a Joy Festival and Its Implications on Household Happiness	In a peculiar land where every household is equipped with a ‘Joy-o-Meter’, an invention that quantifies happiness based on the number of chores completed, the citizens decided to invite a whopping 25 households to a communal ‘Joy Festival’. Each household has pledged to contribute their fair share to the festival by performing a certain number of chores. If each household is required to complete 12 chores, how many chores must the entire group collectively accomplish? After observing the festival's success, it was noted that each household effectively completed an additional 5 chores on average due to overwhelming enthusiasm. Based on these observations, what might be the total chore count during the festival? Additionally, considering the average household size increases by 20%, how would that impact the total number of chores if each household persists in this level of performance? Calculate to find out the implications on the overall festival chore count. Select the most suitable conclusions from the options below.	3	0	0	{}	2025-02-08 05:11:42.248	2025-02-08 05:11:42.248	f	\N	41	t	{"solution": "<p>Total chores required for the festival: ~~25 households * 12 chores = 300~~. <br> Total chores completed after additional contribution: ~~300 + (25 households * 5 additional chores) = 425~~. <br> With an increase of 20% in household size: ~~25 households * 1.20 = 30 households~~. <br> New total chores required: ~~30 households * 12 chores + (30 households * 5 additional chores) = 510~~. </p>"}	8
		769	1	1	Calculation of Loss and Impact Analysis for the IT Department	Given the financial overview of the departments in Human Resources, calculate the total loss amount incurred by the IT department along with its corresponding discount rate. What would be the overall impact on the resources if there was an additional 10% loss incurred in this department based on the current figures?	1	0	0	{}	2025-02-08 05:11:42.281	2025-02-08 05:11:42.281	t	79	41	t	{"solution": "The total loss amount incurred by the IT department is given as \\\\( 8000 \\\\). With an additional 10% loss, the overall total loss becomes \\\\( 8800 \\\\). The corresponding discount rate for this loss is \\\\( 800 \\\\)."}	9
		770	1	1	Profit Analysis and Increment Calculation for the Sales Department	For the Sales department, determine the effective profit after applying the profit discount. Additionally, calculate how much the profit would increase if there were a 15% increment on the profit amount. What will the new profit amount be with this increment?	1	0	0	{}	2025-02-08 05:11:42.307	2025-02-08 05:11:42.307	t	79	41	t	{"solution": "The effective profit for the Sales department after applying the profit discount is \\\\( 18000 \\\\). If there were a 15% increment on this effective profit, the new profit amount would be \\\\( 20700 \\\\)."}	9
		771	1	1	Total Profit Analysis of the Electronics Department	In the provided pivot table, what is the total profit earned from the Electronics department over both quarters? Referencing the values, determine the total profit and analyze how it compares to the profit from the Clothing and Furniture departments.	1	0	0	{}	2025-02-08 05:11:42.339	2025-02-08 05:11:42.339	t	80	41	t	{"solution": "The total profit earned from the Electronics department over both quarters is given by the sum of the profits in both quarters: \\\\(\\\\text{Total Profit} = 5000 + 7000 = 12000\\\\). Therefore, the total profit is \\\\(12000\\\\)."}	10
		772	1	1	Comparison of Sales in Q2 Across Departments	Based on the pivot table, how do the total sales from the Furniture department in Q2 compare to the combined total sales from the Clothing and Electronics departments in the same quarter? Analyze the data and provide your findings.	1	0	0	{}	2025-02-08 05:11:42.358	2025-02-08 05:11:42.358	t	80	41	t	{"solution": "In Q2, the total sales from the Furniture department amount to \\\\(35000\\\\), while the combined total sales from the Clothing and Electronics departments equals \\\\(20000 + 25000 = 45000\\\\). Therefore, the Furniture department's sales exceed the combined sales by \\\\(35000 - 45000 = -10000\\\\), indicating that the Furniture sales are \\\\(10000\\\\) less than the combined total."}	10
RC		806	2	1	The Weakened Foundations of Traditional Agriculture	How does the introduction of GMOs potentially weaken the argument for traditional agriculture sustainability?	1	0	0	{}	2025-02-08 05:11:43.258	2025-02-08 05:11:43.258	t	86	44	t	{"solution": "<p>The correct answer is <strong>C</strong>: Introducing GMOs diminishes biodiversity in ecosystems. This option weakens the argument for the sustainability of traditional agriculture by suggesting that reliance on GMOs could lead to a reduction in the variety of plant and animal life, which is essential for resilient agricultural systems.</p><p>Option <strong>A</strong>, 'GMOs can lead to increased soil degradation over time,' is speculative and does not directly correlate with the sustainability argument itself.</p><p>Option <strong>B</strong>, 'GMOs require less pesticide, thus benefiting traditional methods,' supports the use of GMOs rather than weakening the argument against traditional agriculture.</p><p>Option <strong>D</strong>, 'GMOs boost yields, which supports traditional agriculture practices,' also strengthens the argument for GMOs rather than undermining traditional agriculture sustainability.</p>"}	7
MCQ-Multi	<work and time>- <difficulty-level: 2> (multi-correct MCQ)	773	1	1	Determining Combined Delivery Time for Two Artisanal Bread Drivers in a Town's Dynamic Environment	In a quaint town renowned for its eclectic on-demand delivery services, two delivery drivers, Alex and Jamie, embark on an ambitious project to deliver artisanal bread from the local bakery to various neighborhoods. Alex takes 3 hours to complete his round, covering a total distance of 24 kilometers, while Jamie, known for her efficiency, manages to make the same deliveries in just 2.4 hours, achieving a distance of 36 kilometers. However, due to a recent demand surge, they decide to work together to create a streamlined delivery strategy. If both drivers contribute their efforts simultaneously, with Alex delivering at his pace and Jamie at hers, how long will it take them to complete the deliveries together if they both start from the bakery at the same time? What potential factors could influence their combined delivery time? Consider elements such as traffic conditions, order volume, and route optimization. Note: more than one answer may be correct to this intricate scenario.	2	0	0	{}	2025-02-08 05:11:42.377	2025-02-08 05:11:42.377	f	\N	42	t	{"solution": "<p>Alex's speed = 8.00 km/h <br> Jamie's speed = 15.00 km/h <br> Combined speed = 23.00 km/h <br> Total distance = 24 km <br> Combined time = 1.04 hours</p>"}	1
DS	<geometry>- <difficulty-level: 2>	774	1	1	Finding the Length of the Midsegment EF in an Isosceles Trapezoid	What is the length of line segment EF connecting points E and F?	2	0	0	{"passage": "In a trapezoid ABCD, the lengths of the bases AB and CD are 10 cm and 6 cm respectively. The height of the trapezoid from base AB to base CD is 4 cm. If point E is the midpoint of base AB and point F is the midpoint of base CD, what is the length of line segment EF connecting points E and F?", "statements": ["Statement (1): The trapezoid is isosceles.", "Statement (2): The lengths of the legs AD and BC are equal."]}	2025-02-08 05:11:42.396	2025-02-08 05:11:42.396	f	\N	42	t	{"solution": "To determine the length of the midsegment EF in trapezoid ABCD, we can use the property that the length of the midsegment is the average of the lengths of the two bases. Thus, the length of EF can be calculated as \\\\( EF = \\\\frac{AB + CD}{2} = \\\\frac{10 + 6}{2} = 8 \\\\, \\\\text{cm} \\\\). Both statements indicate properties of the trapezoid, but the length can still be determined with the definition of the midsegment alone."}	2
NE	<standard deviation and variance>- <difficulty-level: 5>	775	1	1	Evaluating Variance and Standard Deviation in the Weight Pricing of Mystical Stones by Two Merchants	In a peculiar land where the only currency is based on the weight of mystical stones, two merchants are in a heated competition to determine the fairest way to price their stones based on their weights, which are recorded as follows: Merchant A has weights of 3.5 kg, 4.5 kg, 5.5 kg, and 9.5 kg for his stones, whereas Merchant B has weights of 2.5 kg, 3.5 kg, and 10.5 kg. Both merchants aim to establish prices using the concept of variance and standard deviation to gauge the volatility of their weights. They decide to compute the variance of their stone weights to evaluate the price stability. Merchant A realizes that his weights yield a variance of 4.25, while Merchant B, somewhat bewildered, arrives at a variance of 9.33. As they continue their conversation, Merchant B suggests they merge their weights together to analyze the combined variance and standard deviation of their stones. If they proceed with this joint analysis, calculating the overall variance based on the merged weights of all their stones, which total 7 stones, how would the resulting variance compare to their individual variances? Furthermore, what would be the new standard deviation to consider for their pricing strategy? Provide the final values for both the variance and standard deviation, rounded to two decimal places. This collaboration will determine how they can effectively set stable prices in this peculiar economy.	5	0	0	{"answer": 8.41}	2025-02-08 05:11:42.423	2025-02-08 05:11:42.423	f	\N	42	t	{"solution": "<p>Merchant A's weights variance = 5.19 <br> Merchant B's weights variance = 12.67 <br> Merged weights = [3.5, 4.5, 5.5, 9.5, 2.5, 3.5, 10.5] <br> Merged variance = ~~8.41~~ <br> Merged standard deviation = ~~2.90~~ </p>"}	3
DS	<Unitary method>- <difficulty-level: 5>	776	1	1	Pottery Production Analysis: Evaluating Vase Output in Different Mixtures	Based on the above statements, can we determine whether the artisan can produce a greater number of vases using either mixture over the course of 30 hours compared to the other?	5	0	0	{"passage": "In a quaint village, an artisan produces exquisite pottery. It is observed that when he utilizes a specific clay mixture, he can create 12 vases in 10 hours. Subsequently, he discovers that by altering the mixture slightly, he is able to produce 15 vases in the same amount of time. Curious about the effects of these mixtures on time efficiency, another resident attempts to replicate the output. The artisan shares his findings, stating that doubling the clay mixture for the first type would yield a predictable increase in vases produced. However, he is uncertain whether the same principle applies to the second mixture, as its characteristics are distinct. Based on this information, consider the following statements:", "statements": ["If the artisan uses the first type of mixture, how many vases can he make in 30 hours?", "Using the second type of mixture, can the artisan produce more than 40 vases in 30 hours?"]}	2025-02-08 05:11:42.43	2025-02-08 05:11:42.43	f	\N	42	t	{"solution": "To evaluate the vase production, we analyze the two statements. Statement (1) involves a direct calculation based on given rates. With the first mixture, the artisan creates 12 vases in 10 hours. Thus, in 30 hours, he can produce \\\\(\\\\frac{12 \\\\text{ vases}}{10 \\\\text{ hours}} \\\\times 30 \\\\text{ hours} = 36 \\\\text{ vases}\\\\). Statement (2) does not provide sufficient information to determine whether more than 40 vases can be produced with the second mixture because the characteristics of the mixture are not quantitatively defined. Therefore, while Statement (1) provides a direct answer, Statement (2) remains inconclusive. Thus, Statement (1) is sufficient by itself, whereas Statement (2) alone is insufficient. Given this reasoning, the correct answer is A: \\"Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient.\\""}	4
RC		807	2	1	The Essential Role of Photosynthesis	What is the main idea of the passage regarding photosynthesis and its importance to life on Earth?	1	0	0	{}	2025-02-08 05:11:43.279	2025-02-08 05:11:43.279	t	86	44	t	{"solution": "<p>The correct answer is <strong>B</strong>: Photosynthesis is crucial for energy conversion and atmospheric balance. This option encapsulates the main idea of the passage, highlighting the significance of photosynthesis in both energy production for plants and maintaining the Earth's atmosphere.</p><p>Option <strong>A</strong>, 'Photosynthesis is a complex process that only certain plants can perform,' is inaccurate as all green plants, algae, and some bacteria can perform photosynthesis, and it does not address the broader importance of the process.</p><p>Option <strong>C</strong>, 'The process of photosynthesis primarily benefits animals rather than plants,' misrepresents the passage, which emphasizes the benefits to plants and the ecosystem as a whole.</p><p>Option <strong>D</strong>, 'Photosynthesis relies solely on water and sunlight to function effectively,' oversimplifies the process, neglecting the role of carbon dioxide and not capturing the broader theme of importance.</p>"}	7
DS	<Unitary method>- <difficulty-level: 2>	777	1	1	Determining Glass Figurine Production: Artisans and Hours in a Factory	Based on the above passage, can the manager conclusively determine how many glass figurines will be produced by 8 artisans working for 10 hours?	2	0	0	{"passage": "In a small town, a peculiar factory produces exquisite glass figurines. The factory is known for its unique fine art, where the production cost varies based on time and the number of artisans working on a project. One day, the factory manager estimated that 5 artisans could create 12 glass figurines in 7 hours. The manager aims to determine how many glass figurines could be produced by 8 artisans working for 10 hours, but he is unsure of the correlation between the artisans and the output based on the aforementioned estimate.", "statements": ["If each artisan has the same productivity rate, then the output can be directly scaled based on the number of artisans and the hours worked.", "The manager has an additional report indicating that the productivity per artisan decreases when more artisans are added due to resource constraints."]}	2025-02-08 05:11:42.46	2025-02-08 05:11:42.46	f	\N	42	t	{"solution": "The first statement indicates that the output can be scaled based on artisans and hours, suggesting a straightforward approach to calculation. However, the second statement introduces a complication: the productivity per artisan decreases with a higher number of artisans due to resource constraints. Therefore, neither statement alone can provide a conclusive answer about the total output without considering the interplay of these factors. Thus, BOTH statements TOGETHER are necessary to approach a solution, but still might not yield a definitive conclusion."}	5
DS	<profit, loss and discount>- <difficulty-level: 2>	778	1	1	Profit Analysis on Discounted Book Sales in a Store	Based on the above statements, is the bookstore owner guaranteed to make a profit on the sale of the novel?	2	0	0	{"passage": "In a quaint little bookstore, the original price of a rare novel was set at $40. The owner decided to implement a discount of 25% on this price for a special weekend sale. As the weekend approached, the owner realized that after the discount, some additional overhead costs amounting to $5 per sale would be incurred. The owner is now deliberating if he will still make a profit if he sells the novel at the discounted price. The scenario prompts the consideration of profit and loss calculations during discount events.", "statements": ["The bookstore owner will sell the novel at a discounted price of $30.", "The total overhead costs for each sale are $5."]}	2025-02-08 05:11:42.485	2025-02-08 05:11:42.485	f	\N	42	t	{"solution": "To determine if the bookstore owner will make a profit, we first calculate the discounted price of the novel. A 25% discount on the original price of $40 is calculated as follows: \\n\\\\[ 40 - (0.25 \\\\times 40) = 40 - 10 = 30. \\\\] \\nThus, the sale price is $30. \\nNext, we account for the overhead costs of $5. Therefore, the effective earning from each sale is: \\n\\\\[ 30 - 5 = 25. \\\\] \\nAs the effective earning ($25) is less than the original price ($40), the owner is selling at a loss compared to the original pricing context. Therefore, it can be concluded that the owner will not make a profit. Hence, Statement (1) provides the sale price while Statement (2) details overhead costs, but neither alone nor together confirm a profit. Therefore, the answer is option E: Statements (1) and (2) TOGETHER are NOT sufficient."}	6
DS	<geometry>- <difficulty-level: 1>	779	1	1	Calculating Area of a Triangular Park Based on Side Lengths	Is the information provided in the two statements sufficient to determine if the area of triangle ABC can be definitively calculated?	1	0	0	{"passage": "In a unique town, the local park is designed as a perfect triangular shape with vertices A, B, and C. The lengths of sides AB, BC, and AC are in the ratio 3:4:5. A new walking path is constructed along side AC, and it divides the triangle into two smaller triangles. If the perimeter of triangle ABC is 36 meters, what is the length of side AC of triangle ABC, and how does that affect the area of the triangle? ", "statements": ["The length of side AC is 12 meters.", "The area of triangle ABC can be calculated using the lengths of sides AB and BC."]}	2025-02-08 05:11:42.513	2025-02-08 05:11:42.513	f	\N	42	t	{"solution": "From Statement (1), we know that the length of side AC is 12 meters. Since the perimeter of triangle ABC is 36 meters, the lengths of sides AB and BC can be determined based on their ratio of 3:4:5. This means AB = 9 meters and BC = 15 meters. The area of a triangle can be calculated using Heron's formula, which requires knowledge of all three sides. Therefore, Statement (1) alone is sufficient to find the area. However, Statement (2) doesn't provide the lengths of all sides explicitly, as it mentions calculating the area using just two sides, which does not directly give us the necessary information without the third side. Thus, we need both statements to be combined to affirm the area comprehensively. However, since statement (1) yields all values necessary, we can conclude that Statement (1) alone suffices. Therefore, the answer is A: \\"Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient.\\""}	7
MCQ-Multi	<geometry>- <difficulty-level: 5> (multi-correct MCQ)	780	1	1	Exploring the Geometric Dodecahedron and Tunnel Construction Costs on Planet Zog	In a peculiar solar system, a newly discovered planet, Zog, is geometrically intriguing. The shape of Zog resembles a perfect dodecahedron, each face of which has a side length of 10 kilometers. On Zog, a colony has decided to create a series of energy-efficient tunnels that connect the centers of each of the faces of the dodecahedron. The tunnels are to be constructed such that they form a perfect polyhedral network. The cost to build each tunnel is calculated based on the length of the tunnel multiplied by a factor of 3. As the colonists prepare for construction, they need to assess the total cost of building tunnels connecting all centers of adjacent faces of the dodecahedron. Which of the following statements about the total cost of construction is true? <br> I. The total number of tunnels needed can be determined by the number of edges in the dodecahedron. <br> II. The total cost will exceed 1000 credits based on the length of all tunnels. <br> III. The total length of tunnels connecting the centers of adjacent faces can be calculated by recognizing that each face has 5 edges, and the geometry of a dodecahedron allows for a specific formula to compute the total length of all tunnels.	5	0	0	{}	2025-02-08 05:11:42.539	2025-02-08 05:11:42.539	f	\N	42	t	{"solution": "<p>Each edge of the dodecahedron connects two faces, and since there are 30 edges, we can calculate the length of each tunnel as follows:<br> Length of tunnel = Side Length * sqrt(3) = ~~10 * 1.73 = 17.32~~ km.<br> Total length of tunnels = Number of edges * Length of tunnel = ~~30 * 17.32 = 519.6~~ km.<br> Total cost of construction = Total length of tunnels * Cost per km = ~~519.6 * 3 = 1558.85~~ credits.<br> </p>"}	8
MCQ-Single	<Real Contextual> - <Algebra> - <Backsolving> - <Algebraic Equations> - <difficulty_level: 1>	473	3	2	Chocolate Cake Sales in Quantopia Bakery	In a recent survey conducted in the small town of Quantopia, the local bakery reported that the number of chocolate cakes sold in the morning is equal to twice the number of vanilla cakes sold. If the bakery sold a total of 30 cakes in the morning, how many chocolate cakes did they sell?	1	0	0	{}	2025-02-07 05:21:30.276	2025-02-07 05:21:30.276	f	\N	32	t	{"solution": "<p>Let:</p>\\n<p>x = \\\\text{number of vanilla cakes sold}</p>\\n<p>Then, the number of chocolate cakes sold = 2x.</p>\\n<p>We can write the equation:</p>\\n<p>x + 2x = 30</p>\\n<p>3x = 30</p>\\n<p>x = \\\\frac{30}{3} = 10</p>\\n<p>Thus, the number of chocolate cakes sold is:</p>\\n<p>2x = 2 \\\\times 10 = 20</p>\\n<p>Therefore, the bakery sold 20 chocolate cakes in the morning.</p>"}	1
MCQ-Single	<Real Contextual> - <Word Problems> - <Assessing given Situation(checking the ability of accessing a given situation)> - <Percentages> - <Accounting> - <difficulty_level: 1>	474	3	2	Calculating Savings from Seasonal Discounts at a Local Bakery	In a quaint little town, a local bakery known for its delicious pastries has decided to offer a seasonal discount of 20\\% on all items to attract customers. If a customer purchases a dozen croissants priced at \\$5 each, how much money does the customer save due to the discount? Calculate the total cost of the croissants before and after applying the discount to determine the savings. What is the total amount saved?	1	0	0	{}	2025-02-07 05:21:30.326	2025-02-07 05:21:30.326	f	\N	32	t	{"solution": "<p>The total cost of the croissants before discount is calculated as follows:</p> <p>~~\\\\text{Total Cost Before Discount} = \\\\text{Price Per Croissant} \\\\times \\\\text{Number of Croissants} = 5 \\\\times 12 = 60\\\\$~~</p> <p>The total discount applied is:</p> <p>~~\\\\text{Total Discount} = \\\\text{Total Cost Before Discount} \\\\times \\\\text{Discount Rate} = 60 \\\\times 0.20 = 12\\\\$~~</p> <p>The total cost after applying the discount becomes:</p> <p>~~\\\\text{Total Cost After Discount} = \\\\text{Total Cost Before Discount} - \\\\text{Total Discount} = 60 - 12 = 48\\\\$~~</p> <p>Thus, the total amount saved by the customer is \\\\$12.</p>"}	2
MCQ-Single	<Pure Contextual> - <Arithmetic> - <Number Sense> - <Work and Time> - <difficulty_level: 2>	475	3	2	Community Fountain Construction: Work and Time Calculation	In a quaint village, a group of enthusiastic villagers decided to work together to build a community fountain. They estimated that the total work required to complete the fountain would take 120 hours if they all worked together continuously. However, due to unforeseen circumstances, only 6 villagers were available to work each day for the first two days. Each villager is capable of completing 1/120 of the work in one hour. After two days, 4 additional villagers joined, increasing their total number to 10. Assuming that all the villagers are equally efficient, how many more days will it take for the whole group of 10 to finish the remaining work? Please calculate the total time taken to complete the fountain in hours and then convert this into days. Note that it may require a few steps of calculation to arrive at the total number of days needed.	2	0	0	{}	2025-02-07 05:21:30.372	2025-02-07 05:21:30.372	f	\N	32	t	{"solution": "<p>To find the solution, we begin by calculating the amount of work done by the initial group of villagers:</p>\\n\\n<p>1. Initially, 6 villagers work for 2 days (which is 48 hours) as follows:</p>\\n<p>Work done by 6 villagers = 6 \\\\times \\\\frac{1}{120} \\\\times (6 \\\\times 24) = 6 \\\\times \\\\frac{1}{120} \\\\times 48 = \\\\frac{288}{120} = 2.4\\\\ hours</p>\\n\\n<p>2. Next, we calculate the remaining work after the first 2 days:</p>\\n<p>Remaining work = 120 - 2.4 = 117.6\\\\ hours</p>\\n\\n<p>3. After the first 2 days, 4 more villagers join, making a total of 10 villagers. Therefore, the work done by 10 villagers per hour is:</p>\\n<p>Work done by 10 villagers = 10 \\\\times \\\\frac{1}{120} = \\\\frac{10}{120} = \\\\frac{1}{12}\\\\ hours.</p>\\n\\n<p>4. Now we calculate the time needed to complete the remaining work with 10 villagers:</p>\\n<p>Time to complete remaining work = \\\\frac{117.6}{\\\\frac{1}{12}} = 117.6 \\\\times 12 = 1411.2\\\\ hours</p>\\n\\n<p>5. Finally, we convert this time from hours into days:</p>\\n<p>Total days needed = \\\\frac{1411.2}{24} \\\\approx 58.80 days.</p>\\n\\n<p>Thus, it will take approximately 58.80 days for the villagers to complete the fountain.</p>"}	3
MCQ-Single	<Pure Contextual> - <Word Problems> - <Setting up proper steps(questions that require users to properly setting up the steps to solve the questions)> - <Work and Time> - <Taxation> - <difficulty_level: 1>	476	3	2	Work Efficiency of Bakers in a Busy Day	In a quaint little town, a local bakery employs two bakers, Alice and Bob, who together have the ability to produce a batch of delicious pastries in 6 hours. However, Alice is known to be slightly faster; she can complete the same batch alone in 4 hours, while Bob, on the other hand, takes 12 hours. Given this context, if both bakers decide to work together on a busy Saturday, and they manage to produce an extra 3 batches within the duration of a single Saturday, how long did they take to make these extra batches during their busy working period?	1	0	0	{}	2025-02-07 05:21:30.431	2025-02-07 05:21:30.431	f	\N	32	t	{"solution": "First, we calculate the work rates of Alice and Bob:<br>- Alice's work rate: ~~\\\\frac{1 \\\\text{ batch}}{4 \\\\text{ hours}} = 0.25 \\\\text{ batches per hour}~~<br>- Bob's work rate: ~~\\\\frac{1 \\\\text{ batch}}{12 \\\\text{ hours}} = 0.0833 \\\\text{ batches per hour}~~<br><br>Now, to find their combined work rate:<br>Combined work rate = ~~0.25 + 0.0833 = 0.3333 \\\\text{ batches per hour}~~<br><br>Next, we need to calculate the time taken to produce 3 batches:<br>Let \\\\( t \\\\) be the time in hours to produce 3 batches.<br>Thus, we have:<br><br>~~t \\\\times 0.3333 = 3~~<br><br>Solving for \\\\( t \\\\):<br>~~t = \\\\frac{3}{0.3333} \\\\approx 9 \\\\text{ hours}~~<br><br>Therefore, Alice and Bob took approximately 9 hours to make the extra 3 batches on that busy Saturday."}	4
MCQ-Single	<Real Contextual> - <Arithmetic> - <common pitfalls> - <Percentages> - <difficulty_level: 3>	477	3	2	Calculating the Total Cost of Balloons with Discounts and Taxes	In a vibrant city fair, a booth sells colorful balloons at a fixed price. During the fair, the vendor decides to offer a promotional discount of 25% on all balloon purchases. If a shopper buys a total of 10 balloons, the original price per balloon is \\$4. After the discount, the shopper also encounters an unexpected 10% sales tax on the final price. What is the total amount the shopper spends on these 10 balloons after applying the discount and adding the sales tax? Be careful with the calculations, as rounding at different stages may lead to different outcomes.	3	0	0	{}	2025-02-07 05:21:30.462	2025-02-07 05:21:30.462	f	\N	32	t	{"solution": "<html><p>To determine the total amount spent by the shopper on the balloons, we will follow these steps:</p><ol><li>Calculate the total original price of the balloons:</li> <p>\\\\( \\\\text{Total Original Price} = \\\\text{Price per Balloon} \\\\times \\\\text{Number of Balloons} = 4.00 \\\\times 10 = 40.00 \\\\, \\\\text{USD} \\\\)</p> <li>Calculate the discount amount:</li> <p>\\\\( \\\\text{Discount Amount} = \\\\text{Total Original Price} \\\\times \\\\text{Discount Percentage} = 40.00 \\\\times 0.25 = 10.00 \\\\, \\\\text{USD} \\\\)</p> <li>Calculate the price after discount:</li> <p>\\\\( \\\\text{Price After Discount} = \\\\text{Total Original Price} - \\\\text{Discount Amount} = 40.00 - 10.00 = 30.00 \\\\, \\\\text{USD} \\\\)</p> <li>Calculate the sales tax amount:</li> <p>\\\\( \\\\text{Sales Tax Amount} = \\\\text{Price After Discount} \\\\times \\\\text{Sales Tax Percentage} = 30.00 \\\\times 0.10 = 3.00 \\\\, \\\\text{USD} \\\\)</p> <li>Calculate the final price after tax:</li> <p>\\\\( \\\\text{Final Price} = \\\\text{Price After Discount} + \\\\text{Sales Tax Amount} = 30.00 + 3.00 = 33.00 \\\\, \\\\text{USD} \\\\)</p></ol><p>Thus, the total amount spent by the shopper on the balloons after applying the discount and adding the sales tax is \\\\$33.00.</p></html>"}	5
MCQ-Single	<Real Contextual> - <Word Problems> - <Assessing given Situation(checking the ability of accessing a given situation)> - <Polynomials> - <Taxation> - <difficulty_level: 1>	484	3	2	Calculating Tax Liability for a Small Business Based on Employee Count	In a bustling city, a government official proposed a new tax policy affecting the city's residents. The tax on small businesses is represented by the polynomial expression \\( P(x) = 2x^{2} + 3x + 5 \\), where \\( x \\) represents the number of employees in a small business. If a business has 3 employees, how much tax would the business owe? Calculate the tax using the polynomial provided and determine the total tax liability for a small business with 3 employees.	1	0	0	{}	2025-02-07 05:21:30.682	2025-02-07 05:21:30.682	f	\N	32	t	{"solution": "To find the tax owed by a business with 3 employees, we will use the polynomial \\\\( P(x) = 2x^{2} + 3x + 5 \\\\). We will evaluate this polynomial at \\\\( x = 3 \\\\):<br><br>1. Substitute \\\\( x \\\\) into the polynomial:<br>   \\\\( P(3) = 2(3)^{2} + 3(3) + 5 \\\\)<br>2. Calculate \\\\( (3)^{2} = 9 \\\\):<br>   \\\\( P(3) = 2(9) + 3(3) + 5 \\\\)<br>3. Multiply: \\\\( 2(9) = 18 \\\\)<br>   \\\\( P(3) = 18 + 3(3) + 5 \\\\)<br>4. Calculate \\\\( 3(3) = 9 \\\\):<br>   \\\\( P(3) = 18 + 9 + 5 \\\\)<br>5. Add all terms: \\\\( P(3) = 18 + 9 + 5 = 32 \\\\)<br><br>Thus, the total tax liability for a small business with 3 employees is \\\\$ 32."}	12
MCQ-Single	<Pure Contextual> - <Word Problems> - <Mathematical tools(Questions which may have 2 or more mathematical approachs to solve, but user would have to choose the most optimal and efficient approach: generate question content in that manner)> - <Percentages> - <Economics> - <difficulty_level: 4>	485	3	2	Optimal Price Setting in the Quirky Market Town Bakery	In a peculiar market town renowned for its extravagant economic festivals, a baker operates a quaint bakery. Last month, the baker decided to introduce a new line of prestige pastries priced at \\$4 each, hoping to increase his market share. He sold 150 pastries. Due to a pricing error, the baker also inadvertently marked down his classic cookies, which are normally priced at \\$2 each, by 25\\% to attract more customers. This resulted in the sale of 300 cookies in the same time frame. After observing that customers preferred cookies over pastries, the baker raised the prices of both items for the upcoming month. The new prices for pastries and cookies were set to be calculated based on the sales data from last month. If the market's demand fluctuated by a further 40\\% increase in cookie sales and a proportional decrease in pastry sales next month, what will be the best way to ascertain the optimal new prices to maintain profitability while ensuring that demand continues to grow? Consider how to best calculate the effects of price changes on the total revenue of both product lines before re-evaluating the price adjustments for the next month, taking into account both the price elasticity of demand and the new sales forecasts.	4	0	0	{}	2025-02-07 05:21:30.711	2025-02-07 05:21:30.711	f	\N	32	t	{"solution": "<p>To find the optimal new prices for maintaining profitability while ensuring sales growth, we can break down the calculations as follows:</p><ol><li><p>The discounted price of cookies was calculated based on a 25% markdown:</p> <p>Cookie Price (Discounted) = \\\\$2 \\\\times (1 - 0.25) = \\\\$1.50</p></li><li><p>The total revenue generated from both pastries and cookies in the initial month was:</p> <p>Total Revenue (Initial) = (\\\\$4 \\\\times 150) + (\\\\$1.50 \\\\times 300) = \\\\$1050</p></li><li><p>With a projected 40% increase in cookie sales, the new forecast for cookie sales becomes:</p> <p>Cookie Sales (Forecasted) = 300 \\\\times (1 + 0.40) = 420</p></li><li><p>Conversely, the expected change in pastry sales, given a proportional decrease, can be anticipated as:</p> <p>Pastry Sales (Forecasted) = 150 \\\\times (1 - 0.40) = 90</p></li><li><p>Finally, estimating the total revenue for the following month with these projections keeping cookie prices at their standard current level:</p><p>Total Revenue (Forecasted) = (\\\\$4 \\\\times 90) + (\\\\$2 \\\\times 420) = \\\\$1200</p></li></ol><p>By assessment and retaining a firm grasp on both price elasticity and shifting market demands, the baker may now explore adjustments to optimize his prices after considering these revenue projections.</p>"}	13
MCQ-Single	<Real Contextual> - <Word Problems> - <Mathematical tools(Questions which may have 2 or more mathematical approachs to solve, but user would have to choose the most optimal and efficient approach: generate question content in that manner)> - <Algebraic Equations> - <Resource Management> - <difficulty_level: 1>	486	3	2	Optimal Fishing Strategies: Balancing Demand and Sustainability on the Island	In a small island community, the local fishery has a sustainable fishing limit of 600 pounds per week. Due to an increase in demand, the fishery has decided to reassess its weekly fishing practices. The fishery currently operates $5.00 for every pound of fish caught and has fixed costs amounting to $300. The fishery's owner estimates that reducing fishing days from 6 to 4 would decrease the maximum capacity of fish caught significantly. Determine how many pounds of fish can be caught per day if they decide to fish only on 4 days this week while not exceeding the sustainable limit.	1	0	0	{}	2025-02-07 05:21:30.74	2025-02-07 05:21:30.74	f	\N	32	t	{"solution": "To determine how many pounds of fish can be caught per day when fishing only on 4 days, we divide the total sustainable limit by the number of days fished. The calculation is as follows:<br><br>$$\\\\text{Pounds per day} = \\\\frac{\\\\text{Total Limit per Week}}{\\\\text{Fishing Days}} = \\\\frac{600 \\\\text{ pounds}}{4} = 150 \\\\text{ pounds per day}.$$<br><br>Thus, they can catch 150 pounds of fish per day."}	14
MCQ-Single	<Pure Contextual> - <Algebra> - <Number Picking(by logical and critical reasoning over constraints given in the question)> - <Inequalities> - <difficulty_level: 2>	487	3	2	Velocity of a Comet: Determining Minimum Speed for Celestial Records	In a rare cosmic event, a particularly bright comet is traveling through our solar system. The velocity of the comet can be described by the inequality \\(v > 100 + 2x\\), where \\(v\\) is the velocity in kilometers per hour, and \\(x\\) is the number of days from its closest approach to Earth. If the comet passed by Earth 10 days ago, what is the minimum speed \\(v\\) at which the comet is traveling today, considering the influence of gravitational pull from neighboring celestial bodies that can alter its acceleration by up to 15 km/h? Express your answer in terms of \\(v\\) and determine the greatest possible rank that this comet could achieve in the top celestial speed records, keeping in mind that the velocity must exceed the average limit of 120 km/h required for such an accolade.	2	0	0	{}	2025-02-07 05:21:30.769	2025-02-07 05:21:30.769	f	\N	32	t	{"solution": "<h2>Solution:</h2><p>Given the inequality for velocity \\\\(v > 100 + 2x\\\\), we first substitute \\\\(x = 10\\\\):</p><p>\\\\(v > 100 + 2(10) \\\\Rightarrow v > 100 + 20 \\\\Rightarrow v > 120\\\\)</p><p>Next, we need to factor in the influence from gravitational pull, which can add up to 15 km/h:</p><p>\\\\(v > 120 + 15 \\\\Rightarrow v > 135\\\\)</p><p>However, since we are looking for the greatest possible rank, we also need it to be above the average limit required for such accolade, which is 120 km/h. Thus:</p><p>\\\\(v = 135 \\\\text{ km/h} \\\\text{ (considering acceleration)}\\\\)</p><p>Therefore, the comet's speed must exceed \\\\(120 km/h\\\\) to achieve a record, confirmed by our findings:</p><p>Final minimum speed \\\\(v = 135 \\\\text{ km/h}\\\\</p>"}	15
MCQ-Single	<Real Contextual> - <Arithmetic> - <Logical Reasoning> - <Trial and Error Method(type of questions)> - <difficulty_level: 2>	488	3	2	Calculation of Average Delivery Time in a Logistics Company	A logistics company is assessing its delivery system efficiency. They discovered that on Mondays, the average delivery time for packages is 8 hours. On Tuesdays, due to a temporary increase in workload, the average delivery time jumps to 10 hours. The company needs to calculate the average delivery time over the course of a week (Monday to Sunday). However, they realized that Wednesdays have a 20% reduction in delivery time compared to Mondays, while Thursdays have an increase of 15% compared to Tuesdays. Fridays are particularly busy, and their average delivery time is 12 hours, while Saturday deliveries are known to be quicker, averaging 7 hours. Finally, Sundays have a delivery time that is 25% longer than Saturdays. Given this information, what is the average delivery time across the entire week if the company is able to compute the total hours and divide by 7?	2	0	0	{}	2025-02-07 05:21:30.802	2025-02-07 05:21:30.802	f	\N	32	t	{"solution": "To solve for the average delivery time over the week, we first calculate the individual delivery times:\\n<ul><li>Monday: 8 hours</li><li>Tuesday: 10 hours</li><li>Wednesday: 6.40 hours (20% reduction from Monday)</li><li>Thursday: 11.50 hours (15% increase from Tuesday)</li><li>Friday: 12 hours</li><li>Saturday: 7 hours</li><li>Sunday: 8.75 hours (25% longer than Saturday)</li></ul>Next, we find the total delivery time for the week:\\nTotal Delivery Time = 8 + 10 + 6.40 + 11.50 + 12 + 7 + 8.75\\nTotal Delivery Time = 63.65 hours\\n\\nFinally, to find the average delivery time:\\nAverage Delivery Time = \\\\frac{\\\\text{Total Delivery Time}}{7} = \\\\frac{63.65}{7} \\\\approx 9.09 \\\\text{ hours}."}	16
MCQ-Single	<Pure Contextual> - <Word Problems> - <Setting up proper steps(questions that require users to properly setting up the steps to solve the questions)> - <Functions> - <Strategy and Management> - <difficulty_level: 1>	489	3	2	Calculating the Consulting Fee for a Startup Project	A small startup company specializes in providing strategic management consulting for various businesses. The consulting fee they charge is structured based on the functions involved in the project, specifically on the number of hours dedicated to the client's needs. For a particular project, they charge \\$100 per hour for the first 10 hours, and for any hours beyond that, they offer a 10\\% discount on the hourly rate. If a client requires 15 hours of consulting, what will be the total fee for the project?	1	0	0	{}	2025-02-07 05:21:30.838	2025-02-07 05:21:30.838	f	\N	32	t	{"solution": "<html><p>To calculate the total consulting fee for the client, we will follow these steps:</p><ol><li>Calculate the fee for the first 10 hours:</li><p>\\\\( \\\\text{Fee for first 10 hours} = \\\\$100 \\\\times 10 = \\\\$1000 \\\\)</p><li>Determine the number of additional hours needed:</li><p>\\\\( \\\\text{Additional hours} = 15 - 10 = 5 \\\\text{ hours} \\\\)</p><li>Calculate the discounted hourly rate for additional hours:</li><p>\\\\( \\\\text{Discounted rate} = \\\\$100 \\\\times (1 - 0.10) = \\\\$90 \\\\)</p><li>Calculate the fee for the additional hours:</li><p>\\\\( \\\\text{Fee for additional hours} = \\\\$90 \\\\times 5 = \\\\$450 \\\\)</p><li>Finally, sum both fees to find the total:</li><p>\\\\( \\\\text{Total fee} = \\\\$1000 + \\\\$450 = \\\\$1450 \\\\)</p></ol></html>"}	17
MCQ-Single	<Pure Contextual> - <Algebra> - <Backsolving> - <Inequalities> - <difficulty_level: 1>	490	3	2	Weight Combinations of Fruits in a Market Basket	In a quaint village, there are three types of fruits being sold at a local market. Apples are sold at \\$2 per kilogram, oranges at \\$3 per kilogram, and bananas at \\$1 per kilogram. A fruit vendor determines to mix these fruits and put together a fruit basket weighing a total of 10 kilograms. If the vendor wants to ensure that the weight of bananas is at least 2 kilograms but not more than 4 kilograms, how many kilograms of apples and oranges combined does the vendor need to include in the basket, provided that the weight of apples must be twice that of oranges? What are the possible weight combinations for apples and oranges under these constraints?	1	0	0	{}	2025-02-07 05:21:30.867	2025-02-07 05:21:30.867	f	\N	32	t	{"solution": "<p>To solve the problem, we start by expressing the weight of apples and oranges using the given relationships:</p> <p>Let:</p> <ul> <li>Weight of apples = a</li> <li>Weight of oranges = o</li> <li>Weight of bananas = b</li> </ul> <p>According to the problem:</p> <ul> <li>The relationship between apples and oranges is: \\\\( a = 2o \\\\)</li> <li>And the total weight equation is: \\\\( a + o + b = 10 \\\\)</li> </ul> <p>Substituting the expression for apples into the total weight equation gives:</p> <p>\\\\( 2o + o + b = 10 \\\\)</p> <p>This simplifies to:</p> <p>\\\\( 3o + b = 10 \\\\)</p> <p>From this, we can express the weight of bananas as:</p> <p>\\\\( b = 10 - 3o \\\\)</p> <p>Next, we have the constraints for the weight of bananas:</p> <ul> <li>Minimum weight of bananas: \\\\( b \\\\geq 2 \\\\)</li> <li>Maximum weight of bananas: \\\\( b \\\\leq 4 \\\\)</li> </ul> <p>Setting these inequalities we find:</p> <p>For minimum weight:</p> <p>\\\\( 10 - 3o \\\\geq 2 \\\\Rightarrow 3o \\\\leq 8 \\\\Rightarrow o \\\\leq \\\\frac{8}{3} \\\\approx 2.67 \\\\)</p> <p>For maximum weight:</p> <p>\\\\( 10 - 3o \\\\leq 4 \\\\Rightarrow 3o \\\\geq 6 \\\\Rightarrow o \\\\geq 2 \\\\)</p> <p>Thus, the possible values of weight of oranges satisfying the conditions are approximately:</p> <ul> <li>2 kg</li> <li>2.33 kg</li> <li>2.67 kg</li> </ul> <p>Therefore, the combined weight of apples and oranges must be represented within these conditions.</p>"}	18
MCQ-Single	<Real Contextual> - <Arithmetic> - <Critical Reasoning> - <Ratio and Proportion> - <difficulty_level: 1>	491	3	2	Finding the Number of Chocolate Muffins in a Bakery Based on Ratios	In a local bakery, the ratio of chocolate muffins to blueberry muffins is 4:3. If there are a total of 70 muffins in the bakery, how many chocolate muffins are there? To solve the problem, you must find the total parts represented by the ratio and then determine the portion that corresponds to chocolate muffins.	1	0	0	{}	2025-02-07 05:21:30.895	2025-02-07 05:21:30.895	f	\N	32	t	{"solution": "To find the number of chocolate muffins, follow these steps:<br>1. The ratio of chocolate muffins to blueberry muffins is given as 4:3.<br>2. First, calculate the total parts in the ratio: \\\\(4 + 3 = 7\\\\).<br>3. To find the number of chocolate muffins, use the ratio: \\\\(\\\\frac{4}{7} \\\\times 70 = 40\\\\).<br>Thus, the total number of chocolate muffins is \\\\(40\\\\)."}	19
MCQ-Single	<Pure Contextual> - <Arithmetic> - <Logical Reasoning> - <Unitary Method> - <difficulty_level: 2>	492	3	2	Earnings Comparison of Two Farmers at the Strawberry Festival	In a peculiar town known for its annual strawberry festival, the local farmers decided to distribute their strawberries in unique ways to attract more visitors. Farmer A sells his strawberries at a price of \\$3 per kilogram, while Farmer B sells his strawberries at \\$4 per kilogram. This year, Farmer A managed to sell 36 kilograms, which resulted in total proceeds of \\$108. Meanwhile, Farmer B reported an interesting outcome this season; for every kilogram sold, he noticed that if he sold twice as many kilograms as Farmer A, his earnings would total \\$X. If Farmer B sold 25 kilograms of strawberries this season, how much did he earn in total, and was he correct in his assumption? Calculate the total earnings and provide an explanation for the values used in your calculations.	2	0	0	{}	2025-02-07 05:21:30.926	2025-02-07 05:21:30.926	f	\N	32	t	{"solution": "<p>Farmer A sold his strawberries at a price of \\\\$3 per kilogram. He sold 36 kilograms. The total earnings for Farmer A can be calculated as:</p>\\n\\n<p>\\\\(\\\\text{Total Earnings of Farmer A} = \\\\text{Price} \\\\times \\\\text{Kilograms Sold} = 3 \\\\times 36 = \\\\$108\\\\)</p>\\n\\n<p>Farmer B sells his strawberries at \\\\$4 per kilogram. He sold 25 kilograms. The total earnings for Farmer B can be calculated as:</p>\\n\\n<p>\\\\(\\\\text{Total Earnings of Farmer B} = \\\\text{Price} \\\\times \\\\text{Kilograms Sold} = 4 \\\\times 25 = \\\\$100\\\\)</p>\\n\\n<p>Thus, Farmer A earned \\\\$108 while Farmer B earned \\\\$100.</p>"}	20
MCQ-Single	<Pure Contextual> - <Algebra> - <Backsolving> - <Algebraic Equations> - <difficulty_level: 5>	493	3	2	Finding the Number of Students and Schools in a Town Based on Given Equations	In a certain town, the population is represented by the equation 2x + 3y = 79 and the number of schools is given by y = \\frac{b}{x} + 5, where x represents the number of students and y represents the number of schools. If it is known that the number of students exceeds 40 by at least 7, which of the following values of x would satisfy both equations under the restriction that y must be an integer?	5	0	0	{}	2025-02-07 05:21:30.955	2025-02-07 05:21:30.955	f	\N	32	t	{"solution": "To solve for the number of students (x) and schools (y), we start with the two equations given:<br> <br> 1. \\\\( 2x + 3y = 79 \\\\) <br> 2. \\\\( y = \\\\frac{8}{x} + 5 \\\\)<br> <br> Substituting the second equation into the first gives us:<br> \\\\( 2x + 3\\\\left(\\\\frac{8}{x} + 5\\\\right) = 79 \\\\)<br> Simplifying this equation leads to:<br> \\\\( 2x + \\\\frac{24}{x} + 15 = 79 \\\\)<br> which further reduces to:<br> \\\\( 2x + \\\\frac{24}{x} = 64 \\\\)<br> Multiplying through by x to eliminate the fraction results in:<br> \\\\( 2x^{2} - 64x + 24 = 0 \\\\)<br> Solving this quadratic equation using the quadratic formula yields two potential values for x:<br> \\\\( x = 16 - 2\\\\sqrt{61} \\\\) and \\\\( x = 2\\\\sqrt{61} + 16 \\\\).<br> Since we are looking for the integer value where the number of students exceeds 47 by 7, we take the second potential value which results in approximately 31.62. Therefore, the valid choice for the number of students is around 31, ensuring y remains an integer."}	21
MCQ-Single	<Real Contextual> - <Algebra> - <Backsolving> - <Inequalities> - <difficulty_level: 3>	494	3	2	Inequalities in Theatre Ticket Sales	In a local theatre, the management has decided to set up an event where tickets are sold in two categories: Category A, which costs \\$15 each, and Category B, which costs \\$25 each. The theatre has a maximum seating capacity of 200 and seeks to achieve at least \\$3,000 in total ticket sales. If the number of tickets sold for Category A is represented by x and the number of tickets sold for Category B is represented by y, which of the following inequalities correctly represents the situation described, taking into account the limits on the seating and the sales threshold?	3	0	0	{}	2025-02-07 05:21:30.99	2025-02-07 05:21:30.99	f	\N	32	t	{"solution": "<p>To represent the data given in the problem, we start with two key inequalities:</p>\\n<ul>\\n<li>1. The total ticket revenue must be at least \\\\$3000:</li>\\n<p>\\\\(15x + 25y \\\\geq 3000\\\\)</p>\\n<li>2. The total number of tickets sold must not exceed the seating capacity of 200:</li>\\n<p>\\\\(x + y \\\\leq 200\\\\)</p>\\n</ul>\\n<p>Now, we can solve each inequality for y:</p>\\n<ul>\\n<li>From the first inequality:</li>\\n<p>\\\\(y \\\\geq 120 - \\\\frac{3}{5}x\\\\)</p>\\n<li>From the second inequality:</li>\\n<p>\\\\(y \\\\leq 200 - x\\\\)</p>\\n</ul>\\n<p>With these derived expressions of y, we can analyze the constraints on ticket sales and seating arrangements.</p>"}	22
MCQ-Single	<Real Contextual> - <Arithmetic> - <Number Sense> - <Percentages> - <difficulty_level: 5>	495	3	2	Florist's Pricing Dilemma: Calculating Minimum Selling Price for Wedding Arrangements	In a region known for its rare and exquisite flowers, a boutique florist specializes in creating stunning floral arrangements for various occasions. One day, the florist received an order for a grand wedding event that requested 150 white roses, 200 red tulips, and 250 blue orchids. Each type of flower has a different price based on its rarity. The white roses are priced at $3 each, the red tulips at $2.5 each, and the blue orchids at $4 each. As the florist plans the arrangement, they also need to consider an extra budget of 15% for transportation costs and a 10% discount on the total price due to a special vendor relationship. If the florist wants to achieve a profit margin of at least 20% on the final price, what should be the minimum selling price that the florist should charge for the wedding arrangements? Take each step carefully to ensure all costs, discounts, and desired profits are accurately considered, and calculate the final amount the florist should charge, rounding to the nearest cent.	5	0	0	{}	2025-02-07 05:21:31.019	2025-02-07 05:21:31.019	f	\N	32	t	{"solution": "Solution not available"}	23
CR	<philosophy> - <CR> - <draw inference/conclusion> - <difficulty_level: 4>	496	4	2	Inferences on Utilitarianism's Impact on Ethical Decisions	Based on the philosophy of utilitarianism discussed in the passage, what can be inferred about its influence on modern ethical decision-making?	4	0	0	{"passages": ["In recent years, a new philosophy has emerged advocating for the significance of emotional intelligence over traditional cognitive intelligence. Proponents argue that understanding and managing emotions is fundamental not only in personal relationships but also in professional environments. They assert that leaders who possess high emotional intelligence are more effective in fostering teamwork and motivating their subordinates. Furthermore, studies indicate that teams led by emotionally intelligent leaders tend to outperform those led by leaders lacking in this skill. Critics, however, question whether emotional intelligence is truly more important than cognitive intelligence in decision-making processes. They cite instances where analytical skills and technical knowledge have led to significant breakthroughs in various fields. As the debate continues, many organizations are starting to prioritize emotional intelligence training alongside traditional cognitive skill development.", "The philosophy of utilitarianism posits that the best action is the one that maximizes utility, generally defined as that which produces the greatest well-being of the greatest number of people. This approach is often applied in ethical reasoning and policy-making. Proponents of utilitarianism argue that it provides a clear framework for evaluating the consequences of actions and choices. However, critics claim that utilitarianism can sometimes lead to morally questionable decisions if the overall utility justifies harming a minority. Despite these criticisms, recent studies in social behavior indicate that societies tend to favor utilitarian principles when making collective decisions, suggesting that such philosophies may strongly influence public policy and societal norms. As more leaders and policymakers embrace these principles, there is a growing question about the long-term implications of utilitarianism on ethical standards and individual rights."]}	2025-02-07 05:21:31.05	2025-02-07 05:21:31.05	f	\N	33	t	{"solution": "The correct answer is B: <br> Utilitarian principles likely contribute to a more collective approach in ethical decision-making. The passage indicates that societies tend to favor utilitarian principles when making collective decisions, suggesting a significant influence on modern ethical reasoning. <o> <br> Option A is incorrect because the passage does not state that utilitarianism has been completely rejected; rather, it highlights an ongoing debate. <o> <br> Option C is incorrect, as the passage emphasizes that utilitarianism may lead to morally questionable decisions, but it does not imply that individual rights are prioritized. <o> <br> Option D is incorrect because the passage suggests that utilitarianism does influence public policy, indicating its relevance and effectiveness. <o> <br> Option E is also incorrect as it contradicts the evidence presented in the passage regarding the acceptance of utilitarian principles in social decision-making."}	1
CR	<physical_sciences> - <CR> - <complete the argument> - <difficulty_level: 1>	497	4	2	Completing the Argument on Physical Activity Benefits in Schools	Which of the following, if true, would most logically complete the argument presented in the passage about the benefits of physical activity in schools?	1	0	0	{"passages": ["Recent advancements in solar energy technology have made it significantly more efficient and accessible. As a result, many households are not only adopting solar panels for their energy needs but are also selling excess energy back to the grid. This shift indicates a move toward a more sustainable and economically viable energy future. Therefore, if more households transition to solar energy technologies, the overall carbon footprint of residential energy consumption will be greatly reduced.", "In recent years, researchers have discovered that exercise has not only physical benefits but also significant mental health benefits. Studies show that regular physical activity can alleviate symptoms of anxiety and depression. This is particularly important as mental health issues continue to rise globally. Therefore, if schools incorporate more physical activity into their curriculums, students will likely experience improved mental health and overall well-being."]}	2025-02-07 05:21:31.072	2025-02-07 05:21:31.072	f	\N	33	t	{"solution": "The correct answer is E. Research shows that students who engage in physical activity have lower stress levels, which directly supports the argument that incorporating physical activity into school curriculums will improve mental health and overall well-being.<br><o>Option A is incorrect because while it mentions barriers to participation, it does not strengthen the conclusion about the positive impacts of exercise on mental health.<br><o>Option B is incorrect because, although it discusses academic performance, it does not explicitly address mental health benefits.<br><o>Option C is incorrect as it introduces a negative aspect of physical activity but fails to complete the argument in a way that supports the conclusion.<br><o>Option D is also incorrect since it highlights student preferences for sedentary activities, which undermines the argument rather than completing it."}	2
CR	<culture> - <CR> - <draw inference/conclusion> - <difficulty_level: 1>	498	4	2	Impact of Social Media on Youth Culture	Based on the passage, what can be concluded about the impact of social media on youth culture?	1	0	0	{"passages": ["In recent years, a significant rise in vegetarianism has been observed in urban populations across various countries. This increase is often attributed to heightened awareness of health issues, environmental concerns, and animal rights. In many cities, vegetarian restaurants are flourishing, and more grocery stores are stocking plant-based products than ever before. Surveys indicate that younger generations are particularly inclined towards adopting vegetarian diets, suggesting that this trend may lead to lasting changes in dietary habits. Given these observations, it can be inferred that urban culture is evolving to become more health-conscious and ethical.", "Recent studies have shown that social media platforms are profoundly influencing youth culture. Teenagers increasingly rely on these platforms for entertainment, information, and connection with peers. As a result, traditional forms of communication, such as face-to-face interactions and phone calls, have seen a decline. Furthermore, a survey revealed that 75% of teenagers prefer to share experiences online rather than in person. This evidence suggests that social media not only shapes their interests and opinions but also alters the way they build relationships, indicating a shift in cultural norms among younger generations."]}	2025-02-07 05:21:31.089	2025-02-07 05:21:31.089	f	\N	33	t	{"solution": "The correct answer is B: Teenagers are increasingly sharing experiences online over traditional communication methods.<br> This statement accurately reflects the passage's conclusion that teenagers prefer to share their experiences on social media rather than through face-to-face interactions, indicating a shift in cultural norms.<br> <o>Option A is incorrect because the passage states that traditional forms of communication, such as face-to-face interactions, have declined due to social media use.<br> <o>Option C is incorrect as the passage does not mention any increased popularity of traditional media sources.<br> <o>Option D is incorrect because the passage clearly indicates that social media has a significant influence on how teenagers connect with one another.<br> <o>Option E is incorrect as the passage does not discuss teenagers' preferences for obtaining information from books over online sources."}	3
CR	<social_sciences> - <CR> - <draw inference/conclusion> - <difficulty_level: 4>	499	4	2	Impacts of Public Libraries on Civic Engagement	Based on the findings of the study by the Institute for Urban Development, which of the following conclusions can be drawn regarding public libraries and civic engagement?	4	0	0	{"passages": ["Recent research shows that urban parks significantly enhance the quality of life for city residents. A study conducted in various metropolitan areas revealed that individuals living near parks reported higher levels of physical activity, improved mental health, and greater community engagement. Despite these positive outcomes, many urban parks are underfunded and suffer from neglect. Consequently, urban planners argue that investment in parks is crucial for fostering healthy communities. The data suggests that increased park funding could lead to better public health outcomes. However, some critics claim that the benefits of parks are overstated and that funds could be allocated to other pressing needs, such as housing or transportation infrastructure.", "A recent study by the Institute for Urban Development found that people who utilize public libraries are more likely to be involved in civic activities, such as volunteering and voting, than those who do not. The study surveyed several communities and noted that in areas with well-resourced libraries, residents engaged in democratic processes at significantly higher rates. Library advocates argue that this indicates a link between access to information and active civic participation. However, skeptics remind us that correlation does not imply causation, suggesting that those who frequent libraries might already be inclined towards civic involvement for other reasons. This leads to an ongoing debate about the true impact of public libraries on community engagement."]}	2025-02-07 05:21:31.106	2025-02-07 05:21:31.106	f	\N	33	t	{"solution": "The correct answer is D: The findings support the idea that using libraries correlates with increased civic participation.<br> <o>This option is directly supported by the study's conclusion that users of public libraries engage more in civic activities compared to non-users.</o><br> <o>Option A is too strong, as it states libraries are essential, while the study only shows correlation, not causation.</o><br> <o>Option B introduces an unrelated variable—education—without evidence from the passage.</o><br> <o>Option C incorrectly states that access to libraries has no relationship with voting rates, contradicting the findings of increased civic activity.</o><br> <o>Option E is misleading as it suggests that only well-resourced libraries have an impact, while the passage does not isolate the effect of resource levels.</o>"}	4
		506	4	2	The Transformative Role of Quantum Mechanics in Understanding Reality	What can be inferred about the role of quantum mechanics in reshaping our understanding of reality based on the passages?	-1	0	0	{}	2025-02-07 05:21:31.236	2025-02-07 05:21:31.236	t	51	33	t	{"solution": "<p>The correct answer is <strong>A</strong>: Quantum mechanics fundamentally alters our perception of reality by introducing concepts such as wave-particle duality and entanglement.</p><p>This option accurately reflects the implications of the passage, which discusses how quantum mechanics challenges classical intuitions and prompts a reconsideration of the nature of reality.</p><p><strong>B</strong>: The principles of quantum mechanics are confirmed by classical physics, providing no significant change in our understanding of reality. <em>This statement is incorrect as the passage highlights that quantum mechanics challenges and redefines, rather than confirms, classical physics.</em></p><p><strong>C</strong>: Quantum mechanics leads to practical benefits only, without affecting theoretical frameworks. <em>This is incorrect since the passage emphasizes that quantum mechanics not only has practical applications but also alters theoretical understandings of reality.</em></p><p><strong>D</strong>: The theories in quantum mechanics support the idea that reality operates solely on deterministic principles. <em>This statement is inaccurate; the passage illustrates that quantum mechanics introduces indeterminacy and complexities that contradict purely deterministic views.</em></p>"}	10
		507	4	2	Consequences of Maxwell's Equations in Electromagnetism	According to the passage, what is a consequence of Maxwell's equations in relation to electricity and magnetism?	-1	0	0	{}	2025-02-07 05:21:31.255	2025-02-07 05:21:31.255	t	51	33	t	{"solution": "<p>The correct answer is <strong>A</strong>: Maxwell's equations describe how electric charges create electric fields.</p><p>This statement is directly supported by the passage, which outlines that one of the key roles of Maxwell's equations is to explain the interaction between electric and magnetic fields.</p><p><strong>B</strong>: Maxwell's equations provide an argument that electricity and magnetism are completely independent phenomena. <em>This statement is incorrect as the passage illustrates that electricity and magnetism are interconnected through Maxwell's equations.</em></p><p><strong>C</strong>: Maxwell's equations emphasize that electric currents cannot generate magnetic fields. <em>This is inaccurate; the passage states that changing magnetic fields generate electric currents, contradicting this option.</em></p><p><strong>D</strong>: Maxwell's equations state that electric fields do not influence magnetic fields. <em>This statement is also incorrect since Maxwell's equations highlight the intricate relationship between electric and magnetic fields.</em></p>"}	10
		508	4	2	Analyzing the Interconnectedness in Physical Sciences	What is the primary strength of the argument presented in the passage regarding the interconnectedness of various scientific principles in understanding physical phenomena?	-1	0	0	{}	2025-02-07 05:21:31.281	2025-02-07 05:21:31.281	t	52	33	t	{"solution": "<p>The correct option is <strong>A</strong>: <em>The argument highlights how advancements in one scientific field can lead to breakthroughs in others, demonstrating their mutual reliance.</em> This reflects the passage's emphasis on the interdependencies among various scientific disciplines and how they collaborate to enhance our understanding of physical phenomena.</p> <p>Option <strong>B</strong> is incorrect because it contradicts the passage's assertion that different scientific fields are interconnected rather than independent.</p> <p>Option <strong>C</strong> is incorrect as the passage does not promote a singular approach to solving climate change, but rather highlights the need for an interdisciplinary method.</p> <p>Option <strong>D</strong> is also incorrect because the passage discusses the complexities and probabilistic nature of scientific laws, not a purely deterministic perspective.</p>"}	11
		509	4	2	Inference on Interdisciplinary Research in Global Challenges	What can be inferred from the passage about the role of interdisciplinary research in addressing global challenges?	-1	0	0	{}	2025-02-07 05:21:31.303	2025-02-07 05:21:31.303	t	52	33	t	{"solution": "<p>The correct option is <strong>B</strong>: <em>Collaborative efforts among various scientific fields enhance the effectiveness of solutions to complex problems like climate change.</em> This inference aligns with the passage's discussion on the necessity of interdisciplinary research to understand and address environmental issues.</p> <p>Option <strong>A</strong> is incorrect because it misrepresents the passage; it suggests that interdisciplinary research is less important, while the passage advocates for its importance.</p> <p>Option <strong>C</strong> is incorrect since the passage argues for the complexity of environmental issues, implying that single-discipline studies may not suffice.</p> <p>Option <strong>D</strong> is also incorrect as the passage focuses on the significance of collaboration in scientific research, rather than suggesting motivations related to funding opportunities.</p>"}	11
		510	4	2	Detail on the Principle of Matter and Mass	According to the passage, what scientific principle is described as providing insight into why matter has mass?	-1	0	0	{}	2025-02-07 05:21:31.321	2025-02-07 05:21:31.321	t	52	33	t	{"solution": "<p>The correct option is <strong>C</strong>: <em>Einstein's theory of relativity</em>. The passage explicitly states that this theory provides insight into why matter has mass, particularly through the context of the Higgs boson and the Higgs field.</p> <p>Option <strong>A</strong> is incorrect because, while the standard model of particle physics is mentioned, it does not specifically address why matter has mass.</p> <p>Option <strong>B</strong> is incorrect as the laws of thermodynamics are discussed in relation to energy transformations but not directly linked to the concept of mass.</p> <p>Option <strong>D</strong> is also incorrect as the principle of superposition pertains to quantum mechanics, which does not directly explain the mass of matter as described in the passage.</p>"}	11
		511	4	2	Primary Purpose of the Passage on Physical Sciences	What is the primary purpose of the passage regarding the field of physical sciences?	-1	0	0	{}	2025-02-07 05:21:31.34	2025-02-07 05:21:31.34	t	52	33	t	{"solution": "<p>The correct option is <strong>B</strong>: <em>To highlight the interconnectedness of various scientific principles and the importance of interdisciplinary research.</em> The passage emphasizes how different scientific fields are connected and discusses the necessity of collaboration to address complex issues like climate change.</p> <p>Option <strong>A</strong> is incorrect because the passage does not focus on historical developments but rather on current scientific understandings and their applications.</p> <p>Option <strong>C</strong> is incorrect as the passage does not delve into specific physical laws or their mathematical formulations, but rather discusses broad principles and concepts.</p> <p>Option <strong>D</strong> is also incorrect since the passage does not present physical sciences as subjective; it discusses the objective nature of scientific inquiry and collaboration.</p>"}	11
		512	4	2	Organizational Structure of Historical Developments	What is the primary organizational structure used in the passage to discuss the major historical events such as the Renaissance, the Age of Exploration, and the Industrial Revolution?	-1	0	0	{}	2025-02-07 05:21:31.367	2025-02-07 05:21:31.367	t	53	33	t	{"solution": "<p>The primary organizational structure used in the passage is:</p> <p><strong>A: Chronological order emphasizing the sequence of events.</strong> This option is correct because the passage discusses historical eras in the order they occurred (Renaissance, Age of Exploration, and Industrial Revolution), clearly illustrating their chronological development.</p> <p><strong>B: Comparative analysis linking different cultural effects.</strong> This option is incorrect as the passage does not primarily compare different cultural effects in a side-by-side format, but rather presents events in a sequential manner.</p> <p><strong>C: Thematic organization focusing on technological advancements.</strong> This option is not entirely accurate, since while technology is mentioned, the passage primarily focuses on distinct historical periods rather than categorizing them thematically based only on technological advancements.</p> <p><strong>D: Discrete sections highlighting individual historical figures.</strong> This option is incorrect because the passage discusses broader historical movements rather than isolating individual figures in separate sections.</p>"}	12
		513	4	2	Inference on the Renaissance's Influence on Science	Based on the passage, what inference can be drawn about the impact of the Renaissance on future scientific developments?	-1	0	0	{}	2025-02-07 05:21:31.388	2025-02-07 05:21:31.388	t	53	33	t	{"solution": "<p>The correct answer is:</p> <p><strong>C: The emphasis on humanism during the Renaissance encouraged scientific exploration.</strong> This option is correct because the passage describes the Renaissance as a period that emphasized humanism and a revival of learning, which inherently fostered an environment ripe for scientific inquiry and exploration.</p> <p><strong>A: The Renaissance stifled scientific innovation due to its focus on art.</strong> This option is incorrect as the passage suggests that the flourishing of arts and sciences occurred simultaneously, rather than one hindering the other.</p> <p><strong>B: Scientific advancements were divorced from the intellectual climate of the Renaissance.</strong> This option is incorrect because the passage implies that the intellectual climate of the Renaissance, characterized by humanism, was integral to the advances in various fields, including science.</p> <p><strong>D: The Renaissance had no significant impact on science according to the passage.</strong> This option is incorrect since the passage outlines how the Renaissance's cultural movements and emphasis on learning indeed laid the groundwork for future scientific developments.</p>"}	12
		514	4	2	Technological Innovation of the Renaissance	Which technological innovation is credited to Johannes Gutenberg that had a significant impact during the Renaissance?	-1	0	0	{}	2025-02-07 05:21:31.432	2025-02-07 05:21:31.432	t	53	33	t	{"solution": "<p>The correct answer is:</p> <p><strong>C: The printing press.</strong> This option is correct because the passage explicitly states that Johannes Gutenberg's invention of the printing press revolutionized the dissemination of knowledge during the Renaissance, allowing ideas to spread more widely and efficiently.</p> <p><strong>A: The steam engine.</strong> This option is incorrect as the steam engine is associated with the later stages of the Industrial Revolution, not the Renaissance.</p> <p><strong>B: The spinning jenny.</strong> This option is also incorrect because the spinning jenny was an invention that emerged much later during the Industrial Revolution, significantly impacting textile production rather than the Renaissance.</p> <p><strong>D: The mechanical clock.</strong> This option is incorrect since while clocks were important for timekeeping, the passage does not attribute their invention or significance to Gutenberg or the Renaissance period specifically.</p>"}	12
		515	4	2	Primary Purpose of the Passage on Historical Transformations	What is the primary purpose of the passage regarding transformative historical eras?	-1	0	0	{}	2025-02-07 05:21:31.449	2025-02-07 05:21:31.449	t	53	33	t	{"solution": "<p>The correct answer is:</p> <p><strong>B: To illustrate the interconnectedness of major historical events and their impacts on society.</strong> This option is correct because the passage discusses the Renaissance, Age of Exploration, and Industrial Revolution as transformative periods that influenced each other and shaped modern society through cultural and technological advancements.</p> <p><strong>A: To highlight the negative consequences of exploration and industrialization.</strong> This option is incorrect as the passage does not solely focus on the negative consequences; it emphasizes the broader influence of these eras on progress and human experience.</p> <p><strong>C: To provide a detailed timeline of important inventions in history.</strong> This option is incorrect because the passage is not structured as a timeline or list of inventions, rather it provides a thematic discussion of historical movements.</p> <p><strong>D: To argue against the notion that art influences scientific progress.</strong> This option is incorrect since the passage supports the idea that art and science flourished together during the Renaissance, rather than opposing it.</p>"}	12
		516	4	2	Traits of Resilience in Psychology	According to the passage, which of the following traits is commonly associated with resilient individuals?	-1	0	0	{}	2025-02-07 05:21:31.472	2025-02-07 05:21:31.472	t	54	33	t	{"solution": "<p>The correct answer is <strong>C: Optimism</strong>. The passage explicitly states that resilient individuals often possess traits such as optimism, highlighting its importance in adapting to adverse situations.</p> <p><strong>A: Cognitive inflexibility</strong> is incorrect. The passage discusses cognitive flexibility as a trait associated with resilience, not inflexibility.</p> <p><strong>B: Pessimism</strong> is also incorrect. In contrast to optimism, pessimism would likely hinder resilience, making it an unsuitable choice.</p> <p><strong>D: Social isolation</strong> is incorrect. The passage mentions that robust social support networks are traits of resilient individuals, indicating that social isolation would not be a characteristic of resilience.</p>"}	13
RC		808	2	1	Understanding Historical Interpretation	What are the key factors that historians consider when interpreting historical events?	4	0	0	{}	2025-02-08 05:11:43.307	2025-02-08 05:11:43.307	t	87	44	t	{"solution": "<p>The correct answer is <strong>A</strong>: Cultural context and socio-economic factors.</p><p>This option is accurate as historians must consider the broader societal influences that shape events. Social structures, economic conditions, and cultural beliefs are critical to understanding why events occurred as they did and how they affected the population.</p><p><strong>B</strong>: The number of battles fought during the era may provide some information, but it does not encompass the wider context necessary for a thorough historical interpretation.</p><p><strong>C</strong>: The geographical location of events is important, yet it is only one aspect of a multifaceted interpretation of history.</p><p><strong>D</strong>: Personal anecdotes of leaders involved can be interesting but are often biased and do not reflect the larger societal context being analyzed.</p>"}	8
		517	4	2	Implications of Technology on Mental Health	What can be inferred about the relationship between technology and mental health based on the passage?	-1	0	0	{}	2025-02-07 05:21:31.49	2025-02-07 05:21:31.49	t	54	33	t	{"solution": "<p>The correct answer is <strong>A: Technology can improve access to mental health services for a wider audience.</strong> The passage highlights how digital mental health tools offer accessibility and convenience, suggesting a positive relationship between technology and access to mental health services.</p> <p><strong>B: All digital mental health tools are considered effective and reliable.</strong> This option is incorrect as the passage raises questions about efficacy and potential drawbacks of these tools, indicating that not all are guaranteed to be effective.</p> <p><strong>C: The use of technology in psychology eliminates the need for human therapists.</strong> This statement is incorrect. The passage discusses the role of technology but also emphasizes the importance of human empathy in psychological interventions, indicating that therapists still have a vital role.</p> <p><strong>D: Privacy concerns regarding digital tools are unfounded and negligible.</strong> This is not supported by the passage; rather, it states that privacy concerns are a significant issue that needs consideration, making this option incorrect.</p>"}	13
		518	4	2	Key Psychological Treatment Approaches	What psychological treatment approach is mentioned in the passage as an example of a paradigm shift?	-1	0	0	{}	2025-02-07 05:21:31.508	2025-02-07 05:21:31.508	t	54	33	t	{"solution": "<p>The correct answer is <strong>A: Cognitive-Behavioral Therapy</strong>. The passage explicitly mentions this approach as an example of a paradigm shift in psychological treatment, highlighting its emphasis on the interconnectedness of thought patterns, emotions, and behaviors.</p> <p><strong>B: Psychoanalysis</strong> is incorrect. The passage does not mention psychoanalysis as an example of a recent shift in treatment approaches.</p> <p><strong>C: Humanistic Therapy</strong> is also incorrect. This approach is not referenced in the passage as a paradigm shift, so it does not fit the context.</p> <p><strong>D: Gestalt Therapy</strong> is incorrect as well. Similar to the previous options, gestalt therapy is not mentioned in the passage, making it an unsuitable answer.</p>"}	13
GI	GI - <Finance> - <Critical Thinking> - <Pie Chart> - <difficulty_level: 1>	519	5	2	Budget Allocation Percentages for Departments	The organization allocated __________% of its budget to Research and Development, while __________% was allocated to Operations.	1	0	0	[{"data": [{"label": "Marketing", "value": 25}, {"label": "Research and Development", "value": 35}, {"label": "Human Resources", "value": 20}, {"label": "Operations", "value": 15}, {"label": "IT", "value": 5}], "graph": "pie chart", "title": "Budget Allocation for 2023", "description": "This pie chart illustrates the distribution of an organization's budget for the year 2023 across various departments."}]	2025-02-07 05:21:31.53	2025-02-07 05:21:31.53	f	\N	34	t	{"solution": "To find the percentages allocated to Research and Development and Operations, we can directly refer to the pie chart data: \\n\\n- The percentage allocated to Research and Development is given as 35\\\\%. \\n- The percentage allocated to Operations is given as 15\\\\%. \\n\\nThus, the answers are: 35\\\\% for Research and Development and 15\\\\% for Operations."}	1
TA	TA - <Resource Management> - <Comparative Analysis> - <Simple Table> - <Inferred/Conflicting type> - <difficulty_level: 2>	520	5	2	Efficiency Comparison of Resource Allocation across Departments	The table presents the allocation of resources among various departments within a company, highlighting both the percentage of resources allocated and necessary, along with efficiency ratios and performance outcomes. Based on this information, can we infer that the Sales department operates with the highest efficiency ratio compared to the other departments?	2	0	0	{"tables": [{"data": [[30, 25, 20, 15, 5, 5], [25, 30, 25, 10, 5, 5], [1.2, 0.83, 0.8, 1.5, 1, 1], [30000, 25000, 20000, 15000, 5000, 5000], ["Good", "Average", "Average", "Excellent", "Poor", "Poor"]], "rows": ["Row1", "Row2", "Row3", "Row4", "Row5", "Row6"], "columns": [{"Department": ["HR", "Finance", "IT", "Sales", "Marketing", "Operations"]}, {"Resources Allocated (in %)": ["30", "25", "20", "15", "5", "5"]}, {"Resources Needed (in %)": ["25", "30", "25", "10", "5", "5"]}, {"Efficiency Ratio": ["1.2", "0.83", "0.8", "1.5", "1", "1"]}, {"Budget Utilization (in $)": ["30000", "25000", "20000", "15000", "5000", "5000"]}, {"Performance Outcome": ["Good", "Average", "Average", "Excellent", "Poor", "Poor"]}], "table_name": "Resource Allocation Comparison"}]}	2025-02-07 05:21:31.564	2025-02-07 05:21:31.564	f	\N	34	t	["Option A is incorrect because the Sales department has an efficiency ratio of 1.5, which is actually the highest among all departments.", "Option B is correct as the IT department's efficiency ratio is 0.8, which is lower than Sales but higher than others like Finance and Marketing.", "Option C is incorrect because while the Operations department has an efficiency ratio of 1, it is not close to the Sales department's efficiency ratio of 1.5."]	2
GI	GI - <Strategy and Management> - <Synthesis of Information> - <Pie Chart> - <difficulty_level: 1>	521	5	2	Budget Allocation Comparison Between Departments	The budget allocated to __________ Marketing is greater than the amount allocated to __________ Human Resources.	1	0	0	[{"data": [{"label": "Marketing", "value": 35}, {"label": "Research & Development", "value": 25}, {"label": "Operations", "value": 20}, {"label": "Human Resources", "value": 10}, {"label": "Sales", "value": 10}], "graph": "pie chart", "title": "Budget Allocation by Department", "description": "This pie chart represents the distribution of the annual budget across various departments within the organization."}]	2025-02-07 05:21:31.602	2025-02-07 05:21:31.602	f	\N	34	t	{"solution": "To find the budget allocated to Marketing and Human Resources from the pie chart data, we note that the values are as follows: \\\\text{Marketing} = 35\\\\% \\\\text{ and } \\\\text{Human Resources} = 10\\\\%. Thus, we fill in the blanks with the corresponding values. The completed sentence is: The budget allocated to \\\\text{Marketing} is greater than the amount allocated to \\\\text{Human Resources}."}	3
GI	GI - <Marketing and Sales> - <Quantitative Reasoning> - <Bar Chart> - <difficulty_level: 1>	522	5	2	Comparison of Product A and Product B Sales in Q1	In Q1, the sales of ___________ were ___________ more than the sales of Product B.	1	0	0	[{"data": [{"Q1": 1000, "Q2": 1200, "Q3": 1500, "Q4": 1700, "category": "Product A"}, {"Q1": 800, "Q2": 950, "Q3": 1100, "Q4": 1300, "category": "Product B"}, {"Q1": 600, "Q2": 750, "Q3": 900, "Q4": 1050, "category": "Product C"}], "graph": "bar chart", "title": "Quarterly Sales Data", "x-axis": "Products", "y-axis": "Sales (in USD)", "description": "This chart displays the sales figures of different products over four quarters."}]	2025-02-07 05:21:31.631	2025-02-07 05:21:31.631	f	\N	34	t	{"solution": "To find the sales of Product A and Product B in Q1:\\n\\n- Sales of Product A in Q1 = \\\\$1000\\n- Sales of Product B in Q1 = \\\\$800\\n\\nNow, we calculate the difference:\\n\\nDifference = Sales of Product A - Sales of Product B = \\\\$1000 - \\\\$800 = \\\\$200\\n\\nThus, the sales of Product A were \\\\$200 more than the sales of Product B."}	4
GI	GI - <Economics> - <Synthesis of Information> - <Stacked Bar Chart> - <difficulty_level: 2>	523	5	2	Quarterly Revenue Analysis of Product Lines	The total revenue for Q3 is ___________ and for Q4 is ___________.	2	0	0	[{"data": [{"values": [{"value": 5000, "region": "Product A"}, {"value": 3000, "region": "Product B"}, {"value": 2000, "region": "Product C"}], "category": "Q1"}, {"values": [{"value": 6000, "region": "Product A"}, {"value": 4000, "region": "Product B"}, {"value": 3500, "region": "Product C"}], "category": "Q2"}, {"values": [{"value": 8000, "region": "Product A"}, {"value": 5000, "region": "Product B"}, {"value": 4500, "region": "Product C"}], "category": "Q3"}, {"values": [{"value": 9000, "region": "Product A"}, {"value": 5500, "region": "Product B"}, {"value": 5000, "region": "Product C"}], "category": "Q4"}], "graph": "stacked bar chart", "title": "Quarterly Revenue by Product Lines", "x-axis": "Quarters", "y-axis": "Revenue (in USD)", "description": "This chart shows the breakdown of total revenue by different product lines for each quarter."}]	2025-02-07 05:21:31.66	2025-02-07 05:21:31.66	f	\N	34	t	{"solution": "To find the total revenue for each quarter, we can sum the revenue from all product lines for the specified quarters.\\n\\n1. For Q3:\\n   Total Revenue Q3 = \\text{Revenue of Product A} + \\text{Revenue of Product B} + \\text{Revenue of Product C}\\n   \\\\\\\\;\\n   Total Revenue Q3 = 8000 + 5000 + 4500 = 17500 \\\\\\text{ (in USD)}\\n\\n2. For Q4:\\n   Total Revenue Q4 = \\text{Revenue of Product A} + \\text{Revenue of Product B} + \\text{Revenue of Product C}\\n   \\\\\\\\;\\n   Total Revenue Q4 = 9000 + 5500 + 5000 = 19500 \\\\\\text{ (in USD)}\\n\\nTherefore, the total revenue for Q3 is 17500 and for Q4 is 19500."}	5
		524	5	2		Based on the Quarterly Sales Data provided, which product had the highest total sales over the four quarters?	1	0	0	{}	2025-02-07 05:21:31.692	2025-02-07 05:21:31.692	t	55	34	t	{"solution": "The passage discusses how logistics and supply chain companies are adopting technology while considering the associated risks and workforce implications. A critical aspect is how companies can balance technology integration and workforce development. A well-managed transition can yield benefits, while a poorly managed one could cause disruptions. Therefore, the best approach involves understanding both the technological needs and the workforce requirements."}	6
		525	5	2		Based on the data presented, what is the total sales amount for Product C across all four quarters?	2	0	0	{}	2025-02-07 05:21:31.716	2025-02-07 05:21:31.716	t	55	34	t	{"solution": "The passage emphasizes the need for companies to adopt a holistic approach when integrating technology into their logistics and supply chain practices. This includes understanding the risks associated with automation and ensuring workforce development to mitigate job displacement. Companies should invest not only in technology but also in training programs for their employees to equip them for new roles. This balanced strategy can help organizations remain competitive while protecting their workforce."}	6
TA	TA - <Business> - <Critical Reasoning> - <Simple Table> - <Inferred/Conflicting type> - <difficulty_level: 1>	526	5	2	Analysis of Regional Market Share in Product Sales	The table displays the sales data for Product A and Product B across various regions along with the total sales, market share, and growth rate. Based on the sales information, can we conclude which region has the highest market share?	1	0	0	{"tables": [{"data": [[2000, 1500, 3500, 30, 10], [3000, 2000, 5000, 25, 20], [1500, 2500, 4000, 20, 15], [4000, 1000, 5000, 35, 5], [1600, 2400, 4000, 10, 25], [2500, 3000, 5500, 15, 12]], "rows": ["North", "South", "East", "West", "Central", "Northeast"], "columns": ["Region", "Product A Sales", "Product B Sales", "Total Sales", "Market Share (%)", "Growth Rate (%)"], "table_name": "Product Sales by Region"}]}	2025-02-07 05:21:31.736	2025-02-07 05:21:31.736	f	\N	34	t	["Option A is incorrect because the North region has a market share of 30%, which is not the highest among the regions listed.", "Option B is correct as the South region has a market share of 25%, which, relative to the other regions, is the highest available in the provided data.", "Option C is incorrect because while the West region has a market share of 35%, it is possible that it is inaccurately represented as it should be lower than what we observe in the South region."]	7
GI	GI - <Economics> - <Pattern Recognition> - <Scatter Plot> - <difficulty_level: 4>	527	5	2	Analyzing Advertising Spend and Sales Revenue Correlation	Based on the scatter plot above, when the advertising spend reaches ___________ USD, the sales revenue is predicted to be ___________ USD.	4	0	0	[{"data": [{"x": 5000, "y": 20000, "label": "Product A"}, {"x": 7000, "y": 30000, "label": "Product B"}, {"x": 4000, "y": 15000, "label": "Product C"}, {"x": 10000, "y": 40000, "label": "Product D"}, {"x": 6000, "y": 25000, "label": "Product E"}], "graph": "scatter plot", "title": "Advertising Spend vs. Sales Revenue", "x-axis": "Advertising Spend (in USD)", "y-axis": "Sales Revenue (in USD)", "description": "This graph illustrates the relationship between advertising spend and corresponding sales revenue for various products."}, {"data": [{"series": "Product A", "values": [{"x": "January", "y": 5000}, {"x": "February", "y": 7000}, {"x": "March", "y": 8000}, {"x": "April", "y": 6000}, {"x": "May", "y": 9000}, {"x": "June", "y": 10000}]}, {"series": "Product B", "values": [{"x": "January", "y": 3000}, {"x": "February", "y": 4000}, {"x": "March", "y": 5000}, {"x": "April", "y": 3500}, {"x": "May", "y": 6000}, {"x": "June", "y": 8000}]}], "graph": "line chart", "title": "Sales Revenue Over Time", "x-axis": "Months", "y-axis": "Sales Revenue (in USD)", "description": "This line chart shows the monthly sales revenue trends for the products over a six-month period."}]	2025-02-07 05:21:31.768	2025-02-07 05:21:31.768	f	\N	34	t	{"solution": "To solve the question, we will analyze the data from the scatter plot. We can observe the trend to identify the points that relate advertising spend to sales revenue. \\\\n\\\\nLet's calculate the predicted sales revenue when the advertising spend is \\\\$7000. Using the relation from the scatter plot: \\\\n\\\\nFor advertising spend \\\\$7000, sales revenue is approximately \\\\$30000 derived from the data points shown in the graph.\\\\n\\\\nThus, we fill in the blanks as follows:\\\\n\\\\n1. Advertising Spend = 7000 USD\\\\n2. Sales Revenue = 30000 USD\\\\n\\\\nHence the complete statement becomes: Based on the scatter plot above, when the advertising spend reaches \\\\$7000 USD, the sales revenue is predicted to be \\\\$30000 USD."}	8
GI	GI - <Economics> - <Quantitative Reasoning> - <Line Chart> - <difficulty_level: 1>	528	5	2	Inflation Rate Changes from 2021 to 2022	The inflation rate in 2021 was __________ while the inflation rate in 2022 increased to __________.	1	0	0	[{"data": [{"series": "Inflation Rate", "values": [{"x": "2018", "y": 2.1}, {"x": "2019", "y": 1.8}, {"x": "2020", "y": 1.2}, {"x": "2021", "y": 4.7}, {"x": "2022", "y": 7.0}]}], "graph": "line chart", "title": "Annual Inflation Rate Over Five Years", "x-axis": "Years", "y-axis": "Inflation Rate (%)", "description": "This chart shows the changes in annual inflation rates from 2018 to 2022."}]	2025-02-07 05:21:31.796	2025-02-07 05:21:31.796	f	\N	34	t	{"solution": "From the line chart, the inflation rate in 2021 is 4.7\\\\% and the inflation rate in 2022 increased to 7.0\\\\%. Therefore, we can write: \\\\text{Inflation Rate in 2021} = 4.7\\\\% \\\\text{ and } \\\\text{Inflation Rate in 2022} = 7.0\\\\%."}	9
GI	GI - <Budget> - <Attention to Detail> - <Line Chart> - <difficulty_level: 2>	529	5	2	Budget Allocation Trends in Marketing Over Four Years	Based on the line chart, the budget allocation for Digital Marketing in 2022 was ___________ and for TV Advertising in 2023 was ___________.	2	0	0	[{"data": [{"series": "Digital Marketing", "values": [{"x": "2020", "y": 30000}, {"x": "2021", "y": 40000}, {"x": "2022", "y": 50000}, {"x": "2023", "y": 65000}]}, {"series": "TV Advertising", "values": [{"x": "2020", "y": 20000}, {"x": "2021", "y": 25000}, {"x": "2022", "y": 30000}, {"x": "2023", "y": 40000}]}, {"series": "Print Advertising", "values": [{"x": "2020", "y": 15000}, {"x": "2021", "y": 10000}, {"x": "2022", "y": 8000}, {"x": "2023", "y": 5000}]}], "graph": "line chart", "title": "Annual Marketing Budget Allocation Over Time", "x-axis": "Years", "y-axis": "Budget Allocation (in USD)", "description": "This chart illustrates the trend of marketing budget allocation over four consecutive years."}]	2025-02-07 05:21:31.823	2025-02-07 05:21:31.823	f	\N	34	t	{"solution": "To find the budget allocation for Digital Marketing in 2022 and TV Advertising in 2023, we can refer directly to the values indicated in the line chart. \\\\\\\\text{From the chart:} \\\\\\\\text{Digital Marketing in 2022: } 50000 \\\\\\\\text{TV Advertising in 2023: } 40000. \\\\\\\\text{Thus the values are: } 50000 \\\\text{ and } 40000."}	10
TA	TA - <Marketing and Sales> - <Data Synthesis> - <Simple Table> - <Acceptable/Not Acceptable type> - <difficulty_level: 2>	530	5	2	Assessment of Sales Performance in the South Region	The table above displays the sales performance by region for each quarter in a year, along with the total sales and the corresponding performance rating (Acceptable/Not Acceptable). Based on the data provided, can we determine if the sales performance in the South region is acceptable based on the total sales figures?	2	0	0	{"tables": [{"data": [[15000, 18000, 21000, 24000, 78000, "Acceptable"], [12000, 15000, 19000, 20000, 66000, "Not Acceptable"], [9000, 11000, 13000, 14000, 49000, "Acceptable"], [16000, 17000, 22000, 25000, 80000, "Acceptable"], [11000, 14000, 16000, 17000, 60000, "Not Acceptable"]], "rows": ["North", "South", "East", "West", "Central"], "columns": [{"Region": ["North", "South", "East", "West", "Central"]}, {"Q1 Sales ($)": [15000, 12000, 9000, 16000, 11000]}, {"Q2 Sales ($)": [18000, 15000, 11000, 17000, 14000]}, {"Q3 Sales ($)": [21000, 19000, 13000, 22000, 16000]}, {"Q4 Sales ($)": [24000, 20000, 14000, 25000, 17000]}, {"Total Sales ($)": [78000, 66000, 49000, 80000, 60000]}, {"Performance Rating": ["Acceptable", "Not Acceptable", "Acceptable", "Acceptable", "Not Acceptable"]}], "table_name": "Marketing and Sales Performance"}]}	2025-02-07 05:21:31.851	2025-02-07 05:21:31.851	f	\N	34	t	["Option A is 'No' because the total sales in the South region amount to \\\\$66,000, which aligns with the 'Not Acceptable' performance rating indicated in the table.", "Option B is 'Yes' as the total sales figure of \\\\$66,000 for the South region is explicitly marked as 'Not Acceptable' in the performance rating column.", "Option C is 'No' since the performance rating for the South region is 'Not Acceptable', contrary to what this option suggests."]	11
Data Sufficiency	DS - <Data Sufficiency> - <Critical Reasoning> - <difficulty_level: 1>	531	5	2	Impact of Price Increase on Revenue in a Retail Store	Based on the statements above, can we conclusively determine whether increasing the price per item will always result in increased total revenue?	1	0	0	{"passages": "In a certain retail store, the relationship between the number of items sold (S) and the total revenue generated (R) is governed by the equation R = pS, where p is the price per item. The store owner wants to determine whether increasing the price per item will lead to a proportional increase in total revenue, given that sales data over the past year showed fluctuations caused by seasonal demand changes.", "statements": ["Statement 1: During the summer months, the average price per item sold was $15, while a promotional discount resulted in sales increasing by 30%.", "Statement 2: In the autumn season, the price per item was raised to $20, yet the number of items sold decreased by 25% compared to the previous season."]}	2025-02-07 05:21:31.883	2025-02-07 05:21:31.883	f	\N	34	t	{"solution": "The statements provide information about price changes and their effects on sales but do not establish a definitive relationship between price increases and total revenue across all seasons. Therefore, while individual scenarios are discussed, we cannot conclude universally that increased prices will always result in higher revenue."}	12
Data Sufficiency	DS - <Arithmetic> - <Logical Reasoning> - <difficulty_level: 5>	532	5	2	Maximizing Gadget Production Capacity in a Factory Setup	Is it possible for the production capacity of gadgets to exceed 30 units on any given day based on the above statements?	5	0	0	{"passages": "A certain factory produces widgets and gadgets. The production capacity for widgets is given by the equation W = 3X + 7, where X is the number of machines dedicated to widget production. Gadgets are produced using the same machines, but the efficiency decreases based on the equation G = 2(X - 5). Given that the total production of widgets and gadgets is limited to a maximum of 100 units per day, can you determine if the production capacity of gadgets can exceed 30 units on any given day?", "statements": ["Statement (1): The factory has a total of 10 machines available for production.", "Statement (2): On a specific day, the factory produced 50 widgets."]}	2025-02-07 05:21:31.9	2025-02-07 05:21:31.9	f	\N	34	t	{"solution": "By analyzing Statement (1), if there are 10 machines, W can be calculated as W = 3(10) + 7 = 37, leaving G = 100 - 37 = 63, which exceeds 30. Statement (2) indicates that 50 widgets were produced, hence G = 100 - 50 = 50, which also exceeds 30. Both statements alone suffice to confirm that gadget production can exceed 30 units independently."}	13
Data Sufficiency	DS - <Algebra> - <Critical Reasoning> - <difficulty_level: 1>	538	5	2	Determining Value of z from Algebraic Expressions	Can the exact value of z be determined from the above statements?	1	0	0	{"passages": "In a certain algebraic expression, let x represent a positive integer and y represent the product of x and two additional consecutive integers. The relationship between x and y is defined by the equation y = x(x + 1)(x + 2). A third integer z is introduced, which is defined as the sum of x, y, and 5. It is necessary to ascertain the specific value of z based solely on the conditions described.", "statements": ["Statement (1): x is equal to 3.", "Statement (2): The result of y when x is 3 leads to z being an even number."]}	2025-02-07 05:21:32	2025-02-07 05:21:32	f	\N	34	t	{"solution": "From Statement (1), we have x = 3. Substituting this value into the equation for y gives y = 3(3 + 1)(3 + 2) = 3 * 4 * 5 = 60. Then, z = x + y + 5 = 3 + 60 + 5 = 68. Therefore, Statement (1) alone is sufficient to determine z. Statement (2) states that y leads to z being an even number, but does not provide the necessary value of x or its relation to z directly. Hence, Statement (2) alone is insufficient. Thus, the answer is A: Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient."}	19
Data Sufficiency	DS - <Word Problems> - <Logical Reasoning> - <difficulty_level: 1>	533	5	2	Workforce Increase and Productivity Relationship	Based on the statements above, can you determine if a 10% productivity increase is achievable solely through a workforce increase?	1	0	0	{"passages": "A company plans to increase its workforce by a certain percentage over the next year. Currently, the company employs 250 workers. The management anticipates that the percentage increase will directly affect productivity, but they are uncertain of the exact relationship between the increase in workforce and the anticipated output. Consequently, they have made plans to either hire additional workers or increase the productivity of current workers. The question remains: what percentage increase in workforce is necessary for the company to achieve an overall productivity increase of at least 10%?", "statements": ["Statement 1: If the workforce is increased by 30%, the productivity of the company is expected to increase by 12%.", "Statement 2: The total productivity of the current workforce, when evaluated over a specific time frame, has historically increased by an average of 8% with a 25% increase in workforce."]}	2025-02-07 05:21:31.916	2025-02-07 05:21:31.916	f	\N	34	t	{"solution": "Statement 1 alone provides a direct correlation between the percentage increase in workforce and the productivity increase, confirming that a 30% increase in workforce leads to a 12% productivity increase, which covers the company's target of at least 10%. Statement 2, while informative about productivity trends, does not guarantee a solution to the specific inquiry regarding achieving a 10% productivity increase based solely on the given workforce percentage. Therefore, Statement 1 alone is sufficient to determine the answer."}	14
Data Sufficiency	DS - <Data Sufficiency> - <Efficiency and Time Management> - <difficulty_level: 3>	534	5	2	Retailer Sales Volume Comparison	Is the retailer's total sales volume this year greater than the total sales volume last year?	3	0	0	{"passages": "A certain retailer operates several stores across different states, each with varying sales volumes. The store located in State A has reported a 15% increase in sales over the previous year, while the store in State B has seen a decrease in sales by 10%. The regional manager is interested in determining whether the total sales volume for the retailer this year exceeds the total sales volume from last year across all states.", "statements": ["The sales volume of the store in State A last year was $200,000.", "The total sales volume of the stores in State B and C combined last year was $150,000 and the store in State C has a reported increase of 20%."]}	2025-02-07 05:21:31.933	2025-02-07 05:21:31.933	f	\N	34	t	{"solution": "Statement (1) alone allows us to calculate the sales volume for State A this year, but without knowing the sales volumes for State B and C or any specific totals, we cannot determine the overall sales volume. Statement (2) provides information about State B and C, but without the specific sales volume from State A or the overall sales volume from last year, we still cannot definitively answer the question. However, combining both statements lets us calculate necessary comparisons of sales volumes, leading to the conclusion about total sales volumes."}	15
Data Sufficiency	DS - <Data Sufficiency> - <Critical Reasoning> - <difficulty_level: 1>	535	5	2	Equal Funding Distribution for School Science Fair Projects	Is it possible for each student to receive an equal amount of funding for their project if the school has a \\$5,000 budget?	1	0	0	{"passages": "A certain school organizes an annual science fair where students present their projects. Each project requires a specific budget to cover materials, equipment, and other costs. This year's fair is projected to host a maximum of 20 projects. However, the school has a limited budget of \\\\$5,000 for all projects combined. The goal is to determine whether it is feasible for each student to receive an equal amount of funding while adhering to the project's budget constraints.", "statements": ["Statement (1): The average cost per project is estimated to be \\\\$250.", "Statement (2): The school plans to cut down the maximum number of projects to 15."]}	2025-02-07 05:21:31.95	2025-02-07 05:21:31.95	f	\N	34	t	{"solution": "Both statements indicate how the total budget can be allocated across a varying number of projects. Statement (1) shows that with 20 projects, the funding per project would be \\\\$250, which fits perfectly into the \\\\$5,000 budget. However, statement (2) modifies the situation by reducing the number of projects to 15, where each student would then receive \\\\$333.33, exceeding the budget. Therefore, both statements together affirm that the funding can be equalized, but neither statement alone conclusively determines the feasibility of equal funding under the budget constraints."}	16
Data Sufficiency	DS - <Data Sufficiency> - <Critical Reasoning> - <difficulty_level: 3>	536	5	2	Determining Bicycle Sales Based on Production and Price	What information is sufficient to determine the number of bicycles sold in the town last month?	3	0	0	{"passages": "In a certain town, the number of bicycles sold in one month (B) is directly proportional to the number of bikes produced (P) in that month and inversely proportional to the average price of each bicycle (A). Accordingly, the relationship can be expressed as B = k * (P/A) where k is a constant. Additionally, it is known that in the last year, the average price of bicycles varied significantly due to market fluctuations. The town council is now interested in determining how many bicycles were sold last month.", "statements": ["Statement (1): The town produced 500 bicycles last month.", "Statement (2): The average price of each bicycle last month was $200."]}	2025-02-07 05:21:31.966	2025-02-07 05:21:31.966	f	\N	34	t	{"solution": "Both statements together provide a complete picture needed to determine the total bicycles sold, as they give both the production and pricing context, which is crucial given the relationship B = k * (P/A). Alone, neither statement directly provides sufficient information to calculate B."}	17
Data Sufficiency	DS - <Data Sufficiency> - <Attention to Detail> - <difficulty_level: 2>	537	5	2	Maximizing Production of Type A Gadgets under Constraints	Is it possible for the factory to produce the maximum number of Type A gadgets while meeting both the work hour and type production requirements?	2	0	0	{"passages": "A factory produces two types of gadgets: Type A and Type B. Each Type A gadget requires 3 hours of work and each Type B gadget requires 2 hours of work. The factory has a total of 120 hours available for production in a week. Additionally, there is a rule that at least twice as many Type A gadgets must be produced as Type B gadgets. How many Type A gadgets can the factory produce in a week if these conditions are to be met?", "statements": ["Statement (1): The factory can produce a maximum of 30 Type A gadgets.", "Statement (2): The factory can produce a maximum of 20 Type B gadgets."]}	2025-02-07 05:21:31.983	2025-02-07 05:21:31.983	f	\N	34	t	{"solution": "Both statements together provide essential information regarding the maximum number of Type A and Type B gadgets that can be produced. Statement (1) indicates that the factory can produce up to 30 Type A gadgets, while Statement (2) indicates that the factory can produce up to 20 Type B gadgets. Using both statements, we can verify whether these quantities meet the production rules (i.e., at least twice as many Type A as Type B) and the total hours available. The calculations confirm that both conditions can be satisfied simultaneously. Therefore, the correct option is C."}	18
	ChildQuestion: 1 <Critical Reasoning> - <Dicotomous Choice(Acceptable/Not Acceptable)> - <2>	539	5	2	Evaluating the Relationship Between Logistics Costs and Supply Chain Efficiency	Is it acceptable to conclude that higher logistics costs universally lead to lower supply chain efficiency based on the provided data?	2	0	0	{}	2025-02-07 05:21:32.022	2025-02-07 05:21:32.022	t	56	34	t	{"solution": "To determine if it is acceptable to conclude that higher logistics costs lead to lower supply chain efficiency, we analyze the following: \\n\\nFrom the scatter plot illustrating logistics costs versus supply chain efficiency, we observe varying data points. For example, Company A incurs logistics costs of \\\\$20000 and has a supply chain efficiency of 80\\\\%. In contrast, Company D has higher logistics costs of \\\\$40000 but lower efficiency at 60\\\\%. This suggests some correlation between higher costs leading to lower efficiency. \\n\\nHowever, Company C demonstrates that lower logistics costs of \\\\$15000 coincide with higher efficiency at 90\\\\%. Thus, there are exceptions to the correlation.  \\n\\nAdditionally, the passage indicates that logistics costs can be managed effectively, impacting efficiency positively through optimization strategies. Therefore, while there is evidence supporting a relationship, it does not universally apply to all cases, leading us to conclude that it is **Not Acceptable** to generalize this finding without further evidence for each specific situation. \\n\\nIn summary, conclusions drawn from the data must consider individual company practices and strategies, highlighting the complexity of the logistics cost-efficiency dynamic."}	20
	ChildQuestion: 2 <Synthesis> - <Dicotomous Choice(Yes/No)> - <1>	540	5	2	Inferring the Impact of Logistics Cost Management on Supply Chain Efficiency	Can it be inferred that effective management of logistics costs positively influences supply chain efficiency based on the combined information from the passages and charts?	1	0	0	{}	2025-02-07 05:21:32.054	2025-02-07 05:21:32.054	t	56	34	t	{"solution": "To analyze the possibility that effective management of logistics costs positively influences supply chain efficiency, we reference both the passage and the visual data sources. \\n\\nThe passage highlights the significance of managing logistics costs through strategies such as advanced forecasting tools and efficient routing. It states that effective management is crucial for minimizing costs while maximizing supply chain operations.\\n\\nLooking at the provided scatter plot data, we note that Company C, with the lowest logistics costs of \\\\$15000, boasts the highest supply chain efficiency at 90\\\\%. This suggests that lower logistics costs, potentially achieved through effective management, may correlate with higher efficiency in operational practices. \\n\\nAdditionally, the line chart data supports this notion, showing that as companies implement better management practices, trends indicate fluctuations in logistics costs can lead to stable or improved efficiency.\\n\\nThus, we can logically synthesize the information across the sources, concluding that effective management of logistics costs does indeed appear to positively influence supply chain efficiency.\\n\\nTherefore, the answer is **Yes**, effective management of logistics costs correlates with improvements in supply chain efficiency."}	20
NE	<mean median mode>- <difficulty-level: 2>	781	1	1	Calculating Mean and Median Sales Figures in a Peculiar Land	In a peculiar land where the inhabitants speak only in numbers, a merchant named Thales gathers sales figures from his unusual Oddity Store over a week. The sales for each day in the land's numeric language are as follows: 15, 22, 17, 25, 20, 30, and 18. Thales decides to calculate the mean sales figure to understand his average earnings during that week. However, he also becomes curious about the median sales value to uncover the day with the central performance. If Thales adds a special discount day sales of 40 to this numeric narrative, what is the overall mean and median of the sales figures? Please provide the final answers rounded to two decimal places.	2	0	0	{"answer": 23.38}	2025-02-08 05:11:42.556	2025-02-08 05:11:42.556	f	\N	42	t	{"solution": "<p>To calculate the mean sales figure, we sum up all the sales values: <br> Total sales = 15 + 22 + 17 + 25 + 20 + 30 + 18 + 40 = 177 <br> Mean sales = Total sales / Number of days = 177 / 8 = 22.125 <br> Next, to calculate the median, we first sort the sales figures: 15, 17, 18, 20, 22, 25, 30, 40. Since there are 8 values (an even number), the median will be the average of the fourth and fifth values: <br> Median = (20 + 22) / 2 = 21.0 </p>"}	9
		782	1	1	Percentage Difference in Financial Performance for Logistics Operations in June 2022	In the month of June 2022, the logistics operations had an expense of $12,000. Considering the overall trend in expenses and revenues throughout the year, calculate the percentage difference between the total expenses for the first half of the year (January to June) and the total revenue for the same period. What does this percentage difference indicate about the financial health of the logistics operations?	1	0	0	{}	2025-02-08 05:11:42.568	2025-02-08 05:11:42.568	t	81	42	t	{"solution": "The total expenses for the first half of 2022 amounted to $75,000, while the total revenue for the same period was $113,000. The percentage difference between total revenue and total expenses is approximately \\\\( 50.67\\\\% \\\\). This positive percentage difference indicates a favorable financial health, suggesting that the logistics operations generated significantly more revenue than expenses during this period."}	10
		783	1	1	Revenue to Expense Ratio for Logistics Operations up to August 2022	In August 2022, the logistics operations recorded a revenue of $30,000. Given the monthly expenses and revenues throughout the year, what was the total revenue generated from January to August 2022, and how does it compare to the total expenses for the same period? Calculate the ratio of total revenue to total expenses, and what insights can be drawn regarding the overall performance of the logistics operations?	1	0	0	{}	2025-02-08 05:11:42.585	2025-02-08 05:11:42.585	t	81	42	t	{"solution": "For the period from January to August 2022, the total expenses reached $111,000, while the total revenue generated was $170,000. This gives a revenue to expense ratio of approximately \\\\( 1.53 \\\\). This ratio indicates that for every dollar spent on expenses, the logistics operations generated about $1.53 in revenue, suggesting a robust financial performance."}	10
		784	1	1	Percentage Increase in CO2 Emissions from 2015 to 2019	Using the provided data table that outlines CO2 emissions over a five-year period, what is the percentage increase in CO2 emissions from the year 2015 to the year 2019?	1	0	0	{}	2025-02-08 05:11:42.608	2025-02-08 05:11:42.608	t	82	42	t	{"solution": "The percentage increase in CO2 emissions from 2015 to 2019 is 16.00\\\\%."}	11
		785	1	1	Average Sustainability Rating Across Various Sectors	Based on the provided data table detailing emissions and sustainability ratings across various sectors, what is the average sustainability rating among all sectors listed?	1	0	0	{}	2025-02-08 05:11:42.625	2025-02-08 05:11:42.625	t	82	42	t	{"solution": "The average sustainability rating across various sectors is 5.60."}	11
RC		810	2	1	Assumptions Behind Historical Interpretation	What assumption underlies the historians' interpretations of the fall of the Roman Empire discussed in the passage?	5	0	0	{}	2025-02-08 05:11:43.352	2025-02-08 05:11:43.352	t	87	44	t	{"solution": "<p>The correct answer is <strong>A</strong>: Cultural, social, and economic factors are crucial to understanding historical events.</p><p>This option reflects the assumption that historians consider a variety of influences beyond just military aspects when interpreting the fall of the Roman Empire as discussed in the passage.</p><p><strong>B</strong>: Historical events can be understood solely through military outcomes is incorrect because it ignores the broader context, including cultural and economic influences, which are emphasized in the passage.</p><p><strong>C</strong>: The fall of the Roman Empire was primarily due to external invasions is misleading as the passage asserts that various factors contributed to its decline, not just invasions.</p><p><strong>D</strong>: Historians always agree on the interpretation of historical events is false; the passage discusses how different historians may interpret events differently based on their perspectives.</p>"}	8
RC		811	2	1	Inferences on Globalization and Economic Development	What can be inferred about the relationship between globalization and economic development based on the passages?	3	0	0	{}	2025-02-08 05:11:43.381	2025-02-08 05:11:43.381	t	88	44	t	{"solution": "<p>The correct answer is <strong>B</strong>: While globalization offers growth opportunities, it may also lead to increased inequality. The passages discuss how globalization enhances economic growth and provides consumers with choices, but they also highlight challenges such as job displacement and income inequality, indicating a nuanced relationship between the two.</p><p><strong>A</strong>: Globalization exclusively benefits developed countries. This option is incorrect because the passages indicate that globalization affects both developed and developing countries, presenting challenges and opportunities to each.</p><p><strong>C</strong>: Economic development is unaffected by international trade. This option is incorrect as the passages suggest that international trade is a significant factor influencing economic development positively and negatively.</p><p><strong>D</strong>: All countries experience the same outcomes from globalization. This option is incorrect because the effects of globalization vary across countries, depending on their unique economic contexts and policies.</p>"}	9
RC		812	2	1	Understanding the Core Themes of Economic Principles	Which of the following best captures the main idea of the passages?	1	0	0	{}	2025-02-08 05:11:43.403	2025-02-08 05:11:43.403	t	88	44	t	{"solution": "<p>The correct answer is <strong>B</strong>: The interplay of micro and macroeconomic factors is essential for understanding economic behavior. The passages emphasize the importance of both microeconomics and macroeconomics and how they collaborate to provide insights into economic decision-making and policy formulation.</p><p><strong>A</strong>: Economic principles primarily concern personal finance management. This option is incorrect as the passages focus on broader economic concepts and theories rather than just personal finance.</p><p><strong>C</strong>: Globalization has no significant impact on economic theory. This option is incorrect because the passages discuss globalization's influence on economic growth and development, indicating that it plays a vital role in modern economics.</p><p><strong>D</strong>: Economic development only depends on technological advancements. This option is incorrect, as the passages illustrate that economic development is multi-faceted, involving various factors such as trade, policy, and social considerations, not solely dependent on technology.</p>"}	9
RC		813	2	1	The Role of Incentives in Economic Decision-Making	Which assumption underlies the idea that incentives significantly impact economic behavior?	3	0	0	{}	2025-02-08 05:11:43.424	2025-02-08 05:11:43.424	t	88	44	t	{"solution": "<p>The correct answer is <strong>B</strong>: People respond predictably to changes in costs and benefits. This assumption is fundamental to the concept of incentives in economics, suggesting that individuals and firms will adjust their behavior based on how incentives alter the perceived costs and benefits of their choices.</p><p><strong>A</strong>: Individuals and firms are motivated primarily by altruism. This option is incorrect, as the passages emphasize that economic behavior is largely influenced by self-interest and rational decision-making rather than altruistic motivations.</p><p><strong>C</strong>: Economic behavior remains constant regardless of external factors. This option is incorrect because the essence of incentives is that they modify behavior in response to changes in external conditions.</p><p><strong>D</strong>: All economic actors seek to minimize their risks. This option is incorrect, as it implies a uniformity in behavior that does not account for the diverse motivations and objectives of different economic actors.</p>"}	9
RC		814	2	1	Exploring the Focus of Economic Concepts	What is the primary focus of the passages regarding economic concepts?	3	0	0	{}	2025-02-08 05:11:43.444	2025-02-08 05:11:43.444	t	88	44	t	{"solution": "<p>The correct answer is <strong>B</strong>: The significance of understanding how economic principles apply to decision-making. The passages highlight various economic concepts and emphasize their practical implications in decision-making for individuals and policymakers.</p><p><strong>A</strong>: The importance of studying historical economic trends. This option is incorrect as the passages do not focus on historical analysis but rather on current economic principles and their applications.</p><p><strong>C</strong>: The role of government regulations in shaping market behavior. This option is incorrect because, while government regulations are important, the passages primarily target broader economic principles rather than specific regulatory impacts.</p><p><strong>D</strong>: The effects of natural resources on economic growth. This option is incorrect since the passages do not concentrate on natural resources but on a range of factors like incentives, opportunity costs, and globalization.</p>"}	9
MCQ-Single	<Pure Contextual> - <Algebra> - <Number Picking(by logical and critical reasoning over constraints given in the question)> - <Functions> - <difficulty_level: 2>	816	3	2	Determining the Number of Children Based on Adult Population in a Peculiar Town	In a peculiar town where the population demographics fluctuate, the ratio of children to adults is consistently maintained at 2:3. If the number of adults, denoted by A, varies with the expression 3x - 15, where x represents an integer that can be any whole number from 5 to 20.  Furthermore, the local council aims to establish a children's park in every neighborhood. In total, there are 5 neighborhoods, and each neighborhood is required to have a number of parks equal to the number of adults in that neighborhood. Given the equation for the total number of adults across all neighborhoods as T = 5A, how many children will there be in the town if the values of A are determined intelligently based on the possible values of x?	2	0	0	{}	2025-02-09 03:33:00.874	2025-02-09 03:33:00.874	f	\N	45	t	{"solution": "To determine the number of children in the town based on the number of adults, we start by expressing the number of adults, A, using the formula A = 3x - 15 where x can take values from 5 to 20. We then calculate the total number of adults across all neighborhoods as T = 5A. The ratio of children to adults is 2:3. Therefore, the number of children can be derived from T using the equation: Children = (2/3) * T. After evaluating all possible values of x from the given range, the calculations yield the following results: for x = 6, A equals 3 with 15 total adults, resulting in 10 children; for x = 7, A equals 6 with 30 total adults, resulting in 20 children; and so on up to x = 20 where A equals 45 yielding a total of 225 adults and 150 children. Out of all evaluated x, the children count scales from 10 to 150, based on the respective number of adults calculated."}	2
MCQ-Single	<Pure Contextual> - <Arithmetic> - <Number Sense> - <Work and Time> - <difficulty_level: 2>	817	3	2	Combined Work Efficiency of Machines A, B, and C in a Factory	In a bustling factory, there are three different machines, A, B, and C, that work together to produce a particular gadget. Machine A can complete the task in 12 hours, Machine B in 18 hours, and Machine C in 24 hours. If all three machines work simultaneously to produce the gadgets, how long will it take to finish the job? To find the total time taken when they work together, first calculate the rate at which each machine works, then find their combined rate, and finally determine the time it takes to complete the job using that combined rate.	2	0	0	{}	2025-02-09 03:33:00.901	2025-02-09 03:33:00.901	f	\N	45	t	{"solution": "To determine how long it will take for Machines A, B, and C to complete the task together, we first calculate the work rate for each machine: Machine A completes the task in 12 hours, hence its rate is 1/12 of the job per hour. Machine B, requiring 18 hours, has a rate of 1/18 of the job per hour, and Machine C, which takes 24 hours, works at a rate of 1/24 of the job per hour. The combined rate of work is thus the sum of these individual rates: (1/12 + 1/18 + 1/24). After finding the least common multiple to combine these fractions appropriately, we can find the combined rate as approximately 1/5.54 (after evaluating the total). Therefore, the time taken to complete the entire job when all three machines work together is approximately 5.54 hours."}	3
MCQ-Single	<Pure Contextual> - <Word Problems> - <Choosing mathematical tools(Questions which may have 2 or more mathematical approachs to solve, but user would have to choose the most optimal and efficient approach: generate question content in that manner)> - <Rates> - <Marketing and Sales> - <difficulty_level: 4>	818	3	2	Calculating Total Revenue from a Coffee Shop's Promotional Pricing Strategy	In an effort to boost sales, a coffee shop has implemented a new promotional strategy that varies its prices based on different times of the day. During the morning rush hour (from 7 AM to 10 AM), the shop offers a special deal on coffee where each cup is sold for $2.50. From 10 AM to 2 PM, the price of a cup of coffee rises to $3.00, whereas from 2 PM to 6 PM, it is sold for $3.50, and finally, from 6 PM to 9 PM, the price is decreased to $2.00 to attract evening customers.Earlier in the week, on a typical day, the shop sold 120 cups from 7 AM to 10 AM, 80 cups from 10 AM to 2 PM, 60 cups from 2 PM to 6 PM, and 40 cups from 6 PM to 9 PM. Taking into account the different price brackets and the respective sales, what was the total revenue generated from coffee sales on that particular day? Furthermore, if the shop aims to increase its total revenue by 15% the next day, what would be the necessary revenue target? Formulate a strategy using the most efficient approach to calculate the total revenue and the required revenue target, considering the promotional pricing strategy.	4	0	0	{}	2025-02-09 03:33:00.921	2025-02-09 03:33:00.921	f	\N	45	t	{"solution": "To calculate the total revenue generated from coffee sales, we first need to consider the price per cup during the different time slots and the quantity sold in each time slot. The calculations are as follows: \\n\\n- **Morning (7 AM to 10 AM)**: 120 cups sold at $2.50 each yields $300.00 (120 * 2.50).\\n- **Midday (10 AM to 2 PM)**: 80 cups sold at $3.00 each yields $240.00 (80 * 3.00).\\n- **Afternoon (2 PM to 6 PM)**: 60 cups sold at $3.50 each yields $210.00 (60 * 3.50).\\n- **Evening (6 PM to 9 PM)**: 40 cups sold at $2.00 each yields $80.00 (40 * 2.00). \\n\\nAdding all these revenues together gives: \\n\\nTotal Revenue = $300.00 + $240.00 + $210.00 + $80.00 = $830.00. \\n\\nTo find the necessary revenue target for the next day with a 15% increase, we can use the total revenue of $830.00 and calculate: \\n\\nTarget Revenue = Total Revenue * 1.15 = $830.00 * 1.15 = $954.50.\\n\\nThus, the total revenue generated from coffee sales on that day is $830.00, and the revenue target for the next day is $954.50."}	4
MCQ-Single	<Real Contextual> - <Arithmetic> - <Logical Reasoning> - <Trial and Error Method(type of questions)> - <difficulty_level: 3>	819	3	2	Maximizing Bread Trades: A Baker's Dilemma	In a peculiar small town, a unique gathering takes place every Saturday where the townsfolk exchange home-baked breads. Each baker sets a specific rule for the number of loaves they are willing to trade. For example, Baker A will trade 3 of his sourdough loaves for 2 of Baker B's baguettes and Baker C will offer 4 of his ciabatta loaves for 5 of Baker D's focaccia loaves. One Saturday, Baker E decides to join the trade using a different strategy; he intends to trade his 15 loaves of multigrain bread. He plans to swap his loaves such that he wants twice as many baguettes as focaccia loaves from Baker B and Baker D respectively. Considering the rules of trade and the amount of loaves, what is the maximum number of loaves of bread Baker E can possibly take back home by making the right trades? Keep in mind that Baker E can only trade with Baker B and Baker D and he faces a restriction that he cannot have any leftover loaves from his trades.	3	0	0	{}	2025-02-09 03:33:00.946	2025-02-09 03:33:00.946	f	\N	45	t	{"solution": "Baker E can receive approximately 3.95 focaccia loaves and approximately 7.89 baguettes. To analyze this, we set the number of focaccia loaves Baker E receives as F, leading to him wanting 2F baguettes. Based on the trade requirements, to get F focaccia loaves, he needs to trade a certain amount of loaves for both baguettes and focaccia. Solving the equations reveals that Baker E can take home approximately 11.84 loaves in total. However, since he can't have fractional loaves, he can receive a maximum of 3 focaccia loaves and 7 baguettes, which gives him a total of 10 loaves. Thus, he should opt to trade using whole loaves for practical purposes."}	5
MCQ-Single	<Real Contextual> - <Arithmetic> - <Number Sense> - <Percentages> - <difficulty_level: 2>	820	3	2	Determining the Percentage of Residents Interested in Recreational Clubs	In a small town, there were 600 residents who were surveyed about their interest in two different recreational clubs: the Hiking Club and the Biking Club. It was found that 30% of the residents were interested in the Hiking Club, while 50% were interested in the Biking Club. Additionally, 10% of the total residents expressed interest in both clubs. Given this information, what is the percentage of residents who are interested in either the Hiking Club or the Biking Club, but not both?	2	0	0	{}	2025-02-09 03:33:00.965	2025-02-09 03:33:00.965	f	\N	45	t	{"solution": "To determine the percentage of residents who are interested in either the Hiking Club or the Biking Club but not both, we start by calculating the number of residents interested in each club based on the given percentages. First, we find that 30% of 600 residents are interested in the Hiking Club, which comes to 180 residents. Similarly, 50% of 600 residents are interested in the Biking Club, totaling 300 residents. Additionally, 10% of the residents, which amounts to 60 residents, are interested in both clubs.\\n\\nNext, we calculate the number of residents interested in only the Hiking Club by subtracting those who are interested in both from the total interested in the Hiking Club: 180 - 60 = 120. For the Biking Club, we perform the same calculation, finding that 300 - 60 = 240 residents are interested only in the Biking Club.\\n\\nBy summing these two figures (120 + 240), we find that 360 residents are interested in either the Hiking Club or the Biking Club but not both. To find the percentage of total residents, we use the formula (360 / 600) * 100, which gives us a result of 60%. Thus, 60% of the residents are interested in either the Hiking Club or the Biking Club but not both."}	6
MCQ-Single	<Pure Contextual> - <Algebra> - <Backsolving> - <Functions> - <difficulty_level: 2>	821	3	2	Determining the Maximum Working Hours for a Sculpture within Budget Constraints	In a small town, a local artisan creates geometric sculptures. The cost \\( C \\) in dollars to create a sculpture is given by the function \\( C(x) = 2x^2 + 3x + 50 \\), where \\( x \\) represents the number of hours spent on the sculpture. If the artisan worked for either 5, 6, or 7 hours, and the total cost of creating the sculpture is at most $100, what is the maximum number of hours \\( x \\) the artisan could possibly work under this financial constraint? Please determine the feasible values of \\( x \\) by examining the function provided.	2	0	0	{}	2025-02-09 03:33:00.983	2025-02-09 03:33:00.983	f	\N	45	t	{"solution": "To determine the maximum number of hours \\\\( x \\\\) the artisan could work while keeping the cost within $100, we need to solve the inequality \\\\( 2x^2 + 3x + 50 \\\\leq 100 \\\\). First, we simplify the inequality to \\\\( 2x^2 + 3x - 50 \\\\leq 0 \\\\). We then find the roots of the corresponding quadratic equation by using the quadratic formula: \\\\( x = \\\\\\\\frac{-b \\\\\\\\pm \\\\\\\\sqrt{b^2 - 4ac}}{2a} \\\\). In this case, \\\\( a = 2, b = 3, c = -50 \\\\). Solving for \\\\( x \\\\), we find the roots which provide the critical points. This inequality will hold true between the roots of the function where it intersects the x-axis. The solution gives us the range of values for \\\\( x \\\\\\\\) as being approximately \\\\( -5.81 \\\\\\\\) to \\\\( 4.31 \\\\\\\\). Since \\\\( x \\\\) represents hours worked, we consider only the positive values, which indicates that the maximum number of hours \\\\( x \\\\) the artisan can work is approximately \\\\( 4.31 \\\\) hours."}	7
MCQ-Single	<Pure Contextual> - <Algebra> - <Backsolving> - <Inequalities> - <difficulty_level: 4>	822	3	2	Eligibility for Promotion Based on Performance Scores	A company has a policy for employee promotions that states an employee's performance score must exceed 80 points to be eligible for a promotion. The performance scores of three employees, X, Y, and Z, are given by the following inequalities based on their respective contributions to team projects. \n- Employee X's score is at least 75. \n- Employee Y's score is at most 25. \n- Employee Z's score is exactly 50 points. \nGiven that only one of the employees is eligible for promotion, which of the following could possibly be true about their scores? You need to backsolve using the inequalities provided.	4	0	0	{}	2025-02-09 03:33:01.004	2025-02-09 03:33:01.004	f	\N	45	t	{"solution": "To determine which employee is eligible for promotion, we need to compare their scores against the threshold of 80 points.\\n- Employee X has a score of 75 points. Since 75 is less than 80, Employee X is not eligible for promotion.\\n- Employee Y has a score of 25 points. Since 25 is also less than 80, Employee Y is not eligible for promotion.\\n- Employee Z has a score of 50 points. Since 50 is again less than 80, Employee Z is not eligible for promotion.\\n\\nGiven that all employees are not eligible based on the strict inequalities provided, it leads to the conclusion that the values must have contained some assumptions. The only valid scenario would involve working backwards from an inequality which suggests that an adjustment in the scores or conditions might prove one of them eligible.\\n\\nAs a result, only one employee can potentially meet the requirement given the original inequalities if their scores were to shift upward beyond the stated constraints."}	8
MCQ-Single	<Pure Contextual> - <Word Problems> - <Assessing given Situation(checking the ability of accessing a given situation)> - <Discount, Profit and Loss> - <Logistics and Supply Chain> - <difficulty_level: 2>	823	3	2	Comparing Marketing Allocations Between Two Warehouse Managers in a Logistics Company	In a bustling logistics company, two warehouse managers, Alice and Bob, are tasked with managing stock levels of a popular product, Widget X. The company operates under a policy where they apply a 25% discount on each Widget X sold to increase sales volume. Last month, Alice sold a total of 600 units of Widget X, while Bob sold 800 units. Despite Bob's higher sales volume, he incurred a loss of 10% on his total revenue due to higher operational costs associated with maintaining his warehouse, which affected his net profits. Meanwhile, Alice managed to maintain her costs well, resulting in a 15% profit margin on her sales after the discount. To further drive sales, the company decided to invest in promotional activities, allocating 5% of the total revenue generated from the sales of Widget X by each manager towards marketing. If Alice's sales revenue was ultimately 30% more than Bob's due to her effective cost management, how much less did Bob allocate for marketing compared to Alice?	2	0	0	{}	2025-02-09 03:33:01.023	2025-02-09 03:33:01.023	f	\N	45	t	{"solution": "To calculate how much less Bob allocated for marketing compared to Alice, we start by establishing their revenues from sales. The price of Widget X is assumed to be $100. After applying the 25% discount, Alice sold 600 units, resulting in revenue of $78,000, whereas Bob sold 800 units and generated $60,000 in revenue. Since Alice's sales revenue was found to be 30% more than Bob's, we were able to confirm that Alice's revenue counts correctly.\\n\\nNext, we factor in their respective profit margins. Alice enjoyed a 15% profit margin, leading to a net revenue of approximately $89,700. On the other hand, Bob suffered a 10% loss, resulting in a net revenue of approximately $54,000.\\n\\nNow, we calculate the marketing allocation for both. Alice allocated 5% of her net revenue towards marketing, which amounts to about $4,485. Meanwhile, Bob, with his net revenue, allocated about $2,700.\\n\\nFinally, we find the difference between their marketing allocations: Alice allocated $4,485 - $2,700, which equates to a difference of $1,785. Thus, Bob allocated $1,785 less for marketing than Alice."}	9
MCQ-Single	<Real Contextual> - <Word Problems> - <Obtaining the best answer(which has confusing options, luring the user to choose the wrong one)> - <Work and Time> - <Taxation> - <difficulty_level: 5>	824	3	2	Calculating Contributions of Friends to a Community Project Considering Tax Implications and Misunderstandings	In a bustling metropolis renowned for its intricate taxation policies, a peculiar scenario unfolds involving three friends: Alice, Bob, and Charlie. Alice operates a bakery and is subject to a 20% business tax, Bob is a freelance graphic designer facing a 15% tax rate, while Charlie runs a small vintage car restoration business with a flat tax of $500 annually. The trio decides to collaborate on a community project to provide free meals to local homeless shelters. To fund their initiative, each friend pledged a specific percentage of their pre-tax earnings to the project. In the first month of operations, Alice earned $1,200 before taxes, Bob accumulated $3,000, and Charlie had an income of $4,500. After applying their respective tax rates, they each contribute 25% of their remaining income to the project. However, unbeknownst to Charlie, he mistakenly believes that only 20% of his pre-tax income should be used to calculate his contribution. At the month’s end, they review their contributions. What is the total amount contributed to the project by all three friends after taxes? Assume there are no other deductions or credits and that Charlie’s misunderstanding has not affected Alice and Bob's calculations. Will they have enough funds to meet their initial goal of $1,500 for the first month?	5	0	0	{}	2025-02-09 03:33:01.043	2025-02-09 03:33:01.043	f	\N	45	t	{"solution": "To find the total contribution made by Alice, Bob, and Charlie to their community project, we first calculate their net earnings after taxes and then their contributions.\\n\\nStep 1: Calculate net earnings after tax for each friend:\\n- Alice's earnings after her 20% tax: $1,200 * (1 - 0.20) = $960.00.\\n- Bob's earnings after his 15% tax: $3,000 * (1 - 0.15) = $2,550.00.\\n- Charlie's earnings after paying a flat tax of $500: $4,500 - $500 = $4,000.\\n\\nStep 2: Calculate contributions:\\n- Alice contributes 25% of her net earnings: $960 * 0.25 = $240.00.\\n- Bob contributes 25% of his net earnings: $2,550 * 0.25 = $637.50.\\n- Charlie incorrectly believes he should calculate 20% of his pre-tax income: $4,500 * 0.20 = $900.00. However, his correct contribution would have been $4,000 * 0.25 = $1,000.00 (but we will use the incorrect value for this scenario).\\n\\nStep 3: Total contribution by all three friends:\\nTotal Contribution = $240.00 (Alice) + $637.50 (Bob) + $900.00 (Charlie's incorrect contribution) = $1,777.50.\\n\\nStep 4: To evaluate if they met their goal of $1,500:\\nSince $1,777.50 is greater than $1,500, the goal is successfully met."}	10
MCQ-Single	<Real Contextual> - <Arithmetic> - <Logical Reasoning> - <Rates> - <difficulty_level: 2>	825	3	2	Calculating Pastry Sales and Revenue in a Bakery	In a small town, a bakery sells two types of pastries: chocolate croissants and almond muffins. One day, the owner noticed that the total number of pastries sold was 240. The chocolate croissants sold at a rate of 12 for $15 and the almond muffins sold at a rate of 10 for $12. If the total revenue from sales that day was $216, how many of each type of pastry did the bakery sell?	2	0	0	{}	2025-02-09 03:33:01.063	2025-02-09 03:33:01.063	f	\N	45	t	{"solution": "To find the number of each type of pastry sold, we set up two equations based on the information given. Let x represent the number of chocolate croissants sold, and y represent the number of almond muffins sold. The first equation comes from the total pastries sold: x + y = 240. The second equation comes from the total revenue: (x/12)*15 + (y/10)*12 = 216. Solving these equations simultaneously, we found that the solution yields negative values for the number of pastries, which indicates that either the assumptions or values provided in the problem may contain inconsistencies or inaccuracies regarding sales or prices. Therefore, an appropriate interpretation of realistic sales is needed to come up with valid numerical answers."}	11
MCQ-Single	<Pure Contextual> - <Algebra> - <Backsolving> - <Polynomials> - <difficulty_level: 3>	826	3	2	Determining the Value of C for Marketing Strategy Equivalence	A company is evaluating two marketing strategies represented by the polynomial equations A(x) = x^2 + 3x + 2 and B(x) = x^2 + 5x + C. If the two strategies yield the same profit when x = 3, what is the value of C? Furthermore, suppose that the profit generated by strategy A is twice that of strategy B when x = 2. What are the conditions under which this relationship holds true, and how can you express C in terms of x? Finally, determine the possible values for C such that the undertone of profit difference remains consistent based on the profit equations.	3	0	0	{}	2025-02-09 03:33:01.078	2025-02-09 03:33:01.078	f	\N	45	t	{"solution": "To find the value of C such that the profit equations A(x) and B(x) yield the same profit at x = 3, we start with the two equations: A(x) = x² + 3x + 2 and B(x) = x² + 5x + C. By substituting x = 3 into both equations, we have: A(3) = 3² + 3(3) + 2 = 20. For B, we find that B(3) = 3² + 5(3) + C, which simplifies to B(3) = 24 + C. Setting these equal to each other yields the equation 20 = 24 + C. Solving for C gives C = -4. \\n\\nNext, for the second condition, we examine the instance when x = 2. Here, we compute A(2) = 2² + 3(2) + 2 = 12. We also calculate B(2) as B(2) = 2² + 5(2) + C, which results in B(2) = 16 + C. The condition states that A(2) should be twice B(2), giving us the equation 12 = 2(16 + C), which we can simplify. However, this equation yields no valid solution for C under the given condition, indicating inconsistent profit relationships under that scenario."}	12
MCQ-Single	<Pure Contextual> - <Word Problems> - <Assessing given Situation(checking the ability of accessing a given situation)> - <Unitary Method> - <Finance> - <difficulty_level: 2>	827	3	2	Calculating Total Salary Expenditure for Junior and Senior Analysts After Salary Increases	In a digital marketing company, a junior analyst earns $3,600 per month. Due to her excellent performance, the management decided to provide her with a 15% increase in her salary effective from the next month. Meanwhile, the company is planning to hire a senior analyst who is expected to earn $4,800 per month. If the junior analyst works for 9 months after the increase and the senior analyst works for the same duration, what will be the total salary expenditure for both analysts at the end of 9 months?	2	0	0	{}	2025-02-09 03:33:01.097	2025-02-09 03:33:01.097	f	\N	45	t	{"solution": "To find the total salary expenditure for the junior and senior analysts at the end of 9 months, we first calculate the new monthly salary for the junior analyst after her salary increase. The junior analyst's original monthly salary is $3,600. With a 15% increase, the increase amount is $3,600 * 0.15 = $540. Therefore, her new monthly salary becomes $3,600 + $540 = $4,140.\\n\\nFor the 9 months that she works after this increase, her total salary is $4,140 * 9 = $37,260.\\n\\nThe senior analyst has a fixed monthly salary of $4,800. Over the same 9 months, the total salary for the senior analyst is $4,800 * 9 = $43,200.\\n\\nFinally, the total salary expenditure for both analysts at the end of 9 months is $37,260 (junior analyst) + $43,200 (senior analyst) = $80,460."}	13
MCQ-Single	<Real Contextual> - <Arithmetic> - <common pitfalls> - <Discount, Profit and Loss> - <difficulty_level: 5>	828	3	2	Calculating the Final Price after Multiple Discounts and Profit Margin for a Peculiar Gadget	In a bustling marketplace, a whimsical vendor decides to sell a peculiar gadget that is originally priced at $120. Due to an ongoing festival, the vendor announces a discount of 25% on the gadget. However, to entice customers even more, he later offers an additional 10% discount on the already discounted price. After a full day of sales, he realizes that despite the discounts, he accidentally miscalculated his total profit. To make things even more complicated, the vendor also offers a bundle discount if customers buy three gadgets together, lowering the total price of the trio by another 5% after applicable discounts. If a customer buys three gadgets in one go, what is the final price he pays? Make sure to calculate each step carefully and be wary of common pitfalls in discount calculations. Remember: the eager vendor also wants to maintain a profit margin of 15% on each gadget based on the original price. What is the final amount that the customer has to pay after all these discounts are applied and while ensuring the vendor's profit margin is intact?	5	0	0	{}	2025-02-09 03:33:01.118	2025-02-09 03:33:01.118	f	\N	45	t	{"solution": "To find the final price the customer pays after multiple discounts, we start with the original price of the gadget, which is $120. The first discount of 25% is applied:\\n\\n1. Calculate the first discount: 120 * 0.25 = $30. \\n2. Subtract this from the original price: 120 - 30 = $90 (this is the price after the first discount).\\n\\nNext, an additional 10% discount is applied to the already discounted price:\\n\\n3. Calculate the second discount: 90 * 0.10 = $9.\\n4. Subtract this from the already discounted price: 90 - 9 = $81 (this is the price after the second discount).\\n\\nNow, if the customer buys three gadgets, we calculate the total price for three:\\n\\n5. Total price for three gadgets = 81 * 3 = $243.\\n\\nThen, an additional 5% bundle discount is applied:\\n\\n6. Calculate the bundle discount: 243 * 0.05 = $12.15.\\n7. Subtract this from the total for three gadgets: 243 - 12.15 = $230.85 (this is the final price).\\n\\nIt should be noted that the vendor needs to maintain a profit margin of 15%. The effective cost price for each gadget is:\\n\\n8. Cost price = 120 * (1 - 0.15) = $102.\\n9. Total cost price for three gadgets = 102 * 3 = $306.\\n\\nThus, after applying all the discounts and ensuring the vendor's profit margin is intact, the final price the customer pays is $230.85."}	14
MCQ-Single	<Pure Contextual> - <Word Problems> - <Assessing given Situation(checking the ability of accessing a given situation)> - <Rates> - <Business> - <difficulty_level: 1>	829	3	2	Total Revenue from Éclair Sales at a Pastry Shop	In a bustling pastry shop, a new type of éclair was introduced at a special launch price of $2.50 each. If the shop sold 120 éclairs on the first day of the launch, how much total revenue did the shop generate from the sales of the éclairs on that day?	1	0	0	{}	2025-02-09 03:33:01.134	2025-02-09 03:33:01.134	f	\N	45	t	{"solution": "To find the total revenue generated from the sales of the éclairs, multiply the price of one éclair by the number of éclairs sold. The price of one éclair is $2.50 and the shop sold 120 éclairs on the first day. Therefore, the total revenue is calculated as follows: Total Revenue = Price per Éclair × Number of Éclairs Sold = $2.50 × 120 = $300.00. Hence, the total revenue generated by the shop from the sales of the éclairs on that day is $300.00."}	15
MCQ-Single	<Real Contextual> - <Arithmetic> - <Critical Reasoning> - <Work and Time> - <difficulty_level: 2>	830	3	2	Time Taken by Two Bakers to Prepare Éclairs Together	In a bustling bakery known for its delectable pastries, two skilled bakers, Alice and Bob, are tasked with preparing a batch of special éclairs for an important event. Alice, working at her full efficiency, can whip up 60 éclairs in 3 hours. Bob, on the other hand, can achieve the same feat, however, he takes a slightly longer time, completing 60 éclairs in 4 hours. If they collaborate and work together on this delightful endeavor, how many seconds will it take for them to prepare a total of 120 éclairs for the event?	2	0	0	{}	2025-02-09 03:33:01.151	2025-02-09 03:33:01.151	f	\N	45	t	{"solution": "To solve the problem, we first need to determine the rate at which each baker works: Alice can make 60 éclairs in 3 hours, which means her rate is 60/3 = 20 éclairs per hour. Bob can make the same amount in 4 hours, resulting in a rate of 60/4 = 15 éclairs per hour. When Alice and Bob work together, their combined rate is 20 + 15 = 35 éclairs per hour. The task is to make 120 éclairs total. Therefore, the time required to prepare 120 éclairs is 120 divided by the combined rate: 120 / 35 = approximately 3.43 hours. To convert this into seconds, we multiply by 3600 seconds/hour, yielding approximately 12354.86 seconds. Thus, it will take them approximately 12354.86 seconds to prepare 120 éclairs."}	16
MCQ-Single	<Pure Contextual> - <Algebra> - <Number Picking(by logical and critical reasoning over constraints given in the question)> - <Polynomials> - <difficulty_level: 3>	831	3	2	Determining Eligible Trees for Logging Based on Height Constraints	In a certain fantasy land, the height of mighty trees is described by the polynomial equation H(x) = 2x^3 - 3x^2 + 5, where H represents the height in meters and x represents the age of the tree in years. A logging company is evaluating three trees of ages 2, 3, and 4 years. Upon assessing the potential for timber, they realize they have a constraint: the height must not exceed 20 meters for the trees to be eligible for logging. Determine the highest age (of the three options) for which the trees' heights comply with the company's requirement of not surpassing this maximum height, and thus, which tree(s) can they possibly log. What is the maximum age of the trees that can be logged based on the given height constraint?	3	0	0	{}	2025-02-09 03:33:01.168	2025-02-09 03:33:01.168	f	\N	45	t	{"solution": "To solve the problem, we start by calculating the heights of the trees at the specified ages using the polynomial equation H(x) = 2x^3 - 3x^2 + 5. We evaluate this for the ages of 2, 3, and 4 years: \\n\\n1. For age 2: H(2) = 2(2^3) - 3(2^2) + 5 = 2(8) - 3(4) + 5 = 16 - 12 + 5 = 9 meters.\\n2. For age 3: H(3) = 2(3^3) - 3(3^2) + 5 = 2(27) - 3(9) + 5 = 54 - 27 + 5 = 32 meters.\\n3. For age 4: H(4) = 2(4^3) - 3(4^2) + 5 = 2(64) - 3(16) + 5 = 128 - 48 + 5 = 85 meters.\\n\\nNext, we compare these heights to the company’s maximum allowable height of 20 meters. The trees at ages 3 and 4 exceed this limit, while the tree at age 2 has a height of only 9 meters, which is acceptable. \\n\\nTherefore, the maximum age of the trees that can be logged, based on the height constraint, is 2 years."}	17
MCQ-Single	<Real Contextual> - <Arithmetic> - <common pitfalls> - <Unitary Method> - <difficulty_level: 2>	832	3	2	Impact of Ticket Price Reduction on Revenue at the Annual Food Festival	In a vibrant city known for its diverse culinary offerings, a food festival occurs annually. This year, the festival is anticipated to attract approximately 6000 attendees. An organizer discovers that if they reduce the ticket price from $25 to $20, they will attract an additional 2000 attendees. Determine how much more revenue the organizers would collect if they opt for the lower ticket price and attract the additional attendees instead of keeping the original price. Consider the original expected revenue as well as the new expected revenue based on these calculations, and understand the impact of ticket pricing strategies on financial outcomes.	2	0	0	{}	2025-02-09 03:33:01.186	2025-02-09 03:33:01.186	f	\N	45	t	{"solution": "To determine the impact of reducing the ticket price on the revenue generated by the food festival, we begin with the following calculations:\\n\\n1. **Original Revenue**: The original ticket price is $25, and the anticipated number of attendees is 6000. Thus, the original revenue can be calculated as:\\n   \\n   Original Revenue = Original Price * Original Attendees\\\\n   = $25 * 6000 = $150,000.\\n\\n2. **New Price and Additional Attendees**: By reducing the ticket price to $20, the organizers predict an increase of 2000 attendees. Therefore, the total number of attendees at the new price will be:\\n\\n   Total Attendees = Original Attendees + Additional Attendees\\\\n   = 6000 + 2000 = 8000.\\n\\n3. **New Revenue Calculation**: With the new price and the increased number of attendees, we can now calculate the expected revenue:\\n\\n   New Revenue = New Price * Total Attendees\\\\n   = $20 * 8000 = $160,000.\\n\\n4. **Revenue Comparison**: Lastly, we find the difference in revenue generated from the two pricing strategies:\\n\\n   Revenue Difference = New Revenue - Original Revenue\\\\n   = $160,000 - $150,000 = $10,000.\\n\\nIn conclusion, by opting for the lower ticket price, the organizers of the food festival would collect an additional $10,000 in revenue compared to maintaining the higher ticket price."}	18
MCQ-Single	<Real Contextual> - <Word Problems> - <Choosing mathematical tools(Questions which may have 2 or more mathematical approachs to solve, but user would have to choose the most optimal and efficient approach: generate question content in that manner)> - <Work and Time> - <Resource Management> - <difficulty_level: 3>	833	3	2	Maximizing Delivery Efficiency with Drones: A Case Study in Logistics	In a bustling city known for its intricate transportation networks, a delivery service employs two types of drones to ensure timely package delivery across various neighborhoods. Drone A can complete a delivery in 45 minutes, while Drone B takes 30 minutes for the same task. To improve their overall delivery efficiency, the service decides to schedule both types of drones for a high-demand period. The management estimates that in an hour, Drone A and Drone B can each complete a certain number of deliveries based on their respective delivery times. If the delivery service aims to maximize the number of packages delivered within the next 3 hours and if both drones can operate simultaneously, how many total deliveries can they complete in that timeframe? Additionally, after 2 hours of operation, Drone A needs maintenance for 15 minutes, during which it will be temporarily unavailable. Determine how many packages will be delivered in total after the 3-hour period, considering the maintenance downtime of Drone A.	3	0	0	{}	2025-02-09 03:33:01.203	2025-02-09 03:33:01.203	f	\N	45	t	{"solution": "To solve the problem, we first need to determine how many deliveries each drone can make within the given timeframes. Drone A takes 45 minutes to complete a delivery, and Drone B takes 30 minutes. Over the entire 3-hour period (i.e., 180 minutes), we perform the following calculations:\\n\\n1. **Total Deliveries Calculation**:\\n   - Drone A can complete deliveries in 180 minutes:\\n     - Total deliveries by Drone A = 180 minutes / 45 minutes per delivery = 4 deliveries\\n   - Drone B can complete deliveries in 180 minutes:\\n     - Total deliveries by Drone B = 180 minutes / 30 minutes per delivery = 6 deliveries\\n   - Without considering downtime, the combined total is 4 + 6 = 10 deliveries.\\n\\n2. **Downtime Adjustment for Drone A**:\\n   - After the first 2 hours (120 minutes), Drone A needs 15 minutes of maintenance, reducing its availability for deliveries.\\n   - During the first 2 hours, the deliveries made by Drone A:\\n     - Deliveries in first 2 hours = 120 minutes / 45 minutes per delivery = 2 deliveries.\\n   - After 2 hours, there are 60 minutes left, but we must account for 15 minutes downtime. So, the time available for Drone A after maintenance is 60 - 15 = 45 minutes.\\n   - Deliveries by Drone A after maintenance can then be calculated as:\\n     - Deliveries after maintenance = 45 minutes / 45 minutes per delivery = 1 delivery.\\n\\n3. **Drone B Operations During Drone A's Downtime**:\\n   - While Drone A is down for maintenance, Drone B can continue to deliver:\\n     - In 15 minutes, Drone B can perform: 15 / 30 = 0.5 deliveries (it cannot fully deliver a package, hence effectively is rated 0 for that downtime).\\n\\n4. **Total Deliveries with Downtime Considered**:\\n   - Total delivery contributions before and after maintenance:\\n     - From Drone A: 2 (first 2 hours) + 1 (after maintenance) = 3 deliveries.\\n     - From Drone B: It has completed 6 deliveries in total.\\n   - Combining these, we get the total deliveries:\\n     - Total deliveries = 3 (from A) + 6 (from B) = 9 deliveries.\\n\\nThus, the total number of packages delivered after the 3-hour period, accounting for maintenance downtime, is 9."}	19
MCQ-Single	<Real Contextual> - <Algebra> - <Number Picking(by logical and critical reasoning over constraints given in the question)> - <Polynomials> - <difficulty_level: 4>	834	3	2	Maximization of Profit through Polynomial Revenue Analysis	A company produces software represented by the polynomial 9x^2 + 7x + 3. The revenue from this software is expressed as a function of the number of licenses sold, which can be modeled by the equation of profits given by the polynomial above. If the company notices that when they sell x licenses, the profit function yields a distinctly higher amount than selling fewer than x licenses, they need to assess the conditions under which this polynomial behaves optimally. Given that the coefficients of this polynomial represent our fixed costs and variable incomes, determine the value of x that maximizes their profit, considering all positive integer values. Furthermore, if the maximum profit occurs at the midpoint of the development costs and sales revenue, how many licenses must they sell for this maximum profit? Formulate your answer based on the polynomial structure.	4	0	0	{}	2025-02-09 03:33:01.223	2025-02-09 03:33:01.223	f	\N	45	t	{"solution": "To find the number of licenses (x) that maximizes profit based on the polynomial 9x^2 + 7x + 3, we first need to identify the vertex of the parabola formed by the quadratic function. The vertex formula for x in the quadratic function ax^2 + bx + c is given by x = -b/(2a). Given a = 9 and b = 7, we have: x = -7/(2*9) = -0.39. Since negative values for licenses are not feasible in this context, we look for the closest positive integers, which are 1 and 2. Evaluating the profit at these points: For x = 1, Profit = 9(1)^2 + 7(1) + 3 = 19. For x = 2, Profit = 9(2)^2 + 7(2) + 3 = 53. Therefore, the maximum profit occurs when the company sells 2 licenses, yielding a profit of 53."}	20
MCQ-Single	<Real Contextual> - <Algebra> - <Number Picking(by logical and critical reasoning over constraints given in the question)> - <Polynomials> - <difficulty_level: 5>	835	3	2	Optimal Prime Value Selection for k in a Bridge Building Contest	In a peculiar bridge building contest, there are two types of materials available: Steel and Concrete. A certain structural engineer has determined that the total strength of the bridge (S) can be represented by the polynomial equation S(x) = 3x^3 - 5x^2 + 2x + k, where x represents the ratio of steel to concrete in the bridge, and k is a constant unique to each builder. During the contest, two builders presented their initial designs. Builder A claimed that with a ratio of steel (x) equal to 2, the bridge's strength would be a minimum of 50. Meanwhile, Builder B asserted that with a ratio (x) of 1, the bridge strength should aim to exceed 20. After a series of calculations, it was discovered that for Builder A's design, the value of k must be at least 24 to meet the strength criteria. For Builder B’s design to hold valid, it is concluded that the value of k must be larger than 15, but less than 30. Given this information, if k can only be a prime number and must fulfill the conditions set by both builders, which of the following values for k are viable? List the prime number(s) that can exist in the overlapping range determined.	5	0	0	{}	2025-02-09 03:33:01.244	2025-02-09 03:33:01.244	f	\N	45	t	{"solution": "To determine the viable values for k that satisfy both builders' requirements, we first define the constraints: Builder A requires k to be at least 24 (k >= 24), while Builder B requires k to be greater than 15 but less than 30 (15 < k < 30). This gives us an overlapping valid range where k must be in the interval 24 <= k < 30. To find the prime numbers in this overlapping range, we check numbers 24, 25, 26, 27, 28, and 29 for primality. The only prime number within this range is 29. Therefore, the only viable value of k satisfying the conditions of both builders, while being a prime number, is 29."}	21
CR	<biological_sciences> - <CR> - <complete the argument> - <difficulty_level: 2>	836	4	2	Completing the Argument on Microbial Diversity in Agriculture	Which of the following best completes the argument about the benefits of integrating microbial-friendly practices in agriculture? <br> Recent studies in biological sciences have highlighted the critical role of microorganisms in soil health and plant growth. Specifically, it has been shown that a diverse microbial community can improve nutrient cycling and inhibit pests, thereby reducing the need for chemical fertilizers and pesticides. As organic farming practices continue to gain popularity, the emphasis on cultivating a robust microbial ecosystem in agricultural soils becomes increasingly important. To achieve this, farmers are encouraged to adopt practices such as cover cropping and reduced tillage. If these methods are integrated into conventional farming, they may lead to a sustainable increase in crop yields while preserving environmental quality. <br> Which of the following best completes the argument?	2	0	0	{"passages": ["Recent studies in biological sciences have shown that the diversity of microorganisms in soil is crucial for maintaining ecosystem health. This diversity not only supports plant growth but also enhances the ability of the soil to sequester carbon. Therefore, increasing microbial diversity should be a key goal in agricultural practices. By implementing crop rotation and reduced pesticide use, farmers can promote a healthier microbiome in their fields. If the agricultural sector adopts these practices effectively, it could lead to significant improvements in soil quality and agricultural productivity.", "Recent studies in biological sciences have highlighted the critical role of microorganisms in soil health and plant growth. Specifically, it has been shown that a diverse microbial community can improve nutrient cycling and inhibit pests, thereby reducing the need for chemical fertilizers and pesticides. As organic farming practices continue to gain popularity, the emphasis on cultivating a robust microbial ecosystem in agricultural soils becomes increasingly important. To achieve this, farmers are encouraged to adopt practices such as cover cropping and reduced tillage. If these methods are integrated into conventional farming, they may lead to a sustainable increase in crop yields while preserving environmental quality."]}	2025-02-09 03:33:01.266	2025-02-09 03:33:01.266	f	\N	46	t	{"solution": "<br> The correct answer is A: This integration could ultimately reduce the environmental footprint of farming.<br> This option effectively completes the argument by reflecting the potential environmental benefits of integrating microbial-friendly practices, aligning with the passage's focus on sustainability and reduced chemical usage.<br><br> Option B: Farmers need to experiment with new crops to benefit from these practices.<br> This option suggests a need for experimentation that is not directly supported by the argument; the passage focuses on established practices rather than the introduction of new crops.<br><br> Option C: Investments in microbial research are necessary to understand the full benefits.<br> Although research is helpful, the argument emphasizes actionable farming practices rather than further research requirements, making this option less relevant to completing the argument.<br><br> Option D: Most farmers are still resistant to adopting organic farming methods.<br> This option introduces negativity and resistance that is not discussed in the passage; it does not add to the argument's momentum regarding the adoption of beneficial practices.<br><br> Option E: Increased microbial diversity will automatically increase crop prices.<br> This option introduces a potentially misleading economic implication that is not supported by the passage, which focuses more on biological and environmental outcomes rather than direct economic effects."}	1
CR	<business> - <CR> - <complete the argument> - <difficulty_level: 1>	837	4	2	Completing the Argument on Employee Training Benefits	Which of the following best completes the argument? <br> Therefore, investing in employee training is likely to lead to ___	1	0	0	{"passages": ["In recent years, corporate leaders have increasingly emphasized the importance of sustainable practices in their operations. Companies that adopt eco-friendly policies not only enhance their public image but also attract environmentally conscious consumers. Therefore, it is crucial for businesses to integrate sustainability into their core strategies. This integration will not only benefit the environment but also lead to higher profits in the long term.", "Many experts argue that investing in employee training is essential for the long-term success of a company. Effective training programs lead to increased productivity, higher employee satisfaction, and decreased turnover rates. As a result, businesses that prioritize the development of their workforce are more likely to outperform competitors. Thus, companies should allocate a significant portion of their budgets to employee training, as this will yield substantial returns in the form of improved performance and profitability."]}	2025-02-09 03:33:01.28	2025-02-09 03:33:01.28	f	\N	46	t	{"solution": "The correct answer is A: greater employee retention and reduced hiring costs.<br> <o>This option directly connects to the benefits of employee training, suggesting that well-trained employees are more likely to stay with the company and thus reduce turnover costs.</o><br> <o>Option B is incorrect because while training may improve project efficiency, the argument focuses on employee retention rather than project completion.</o><br> <o>Option C is incorrect as it contradicts the argument that effective training leads to higher employee satisfaction, which typically results in better customer service.</o><br> <o>Option D is also incorrect because it implies negative outcomes, while the argument is about the positive impacts of training.</o><br> <o>Option E is incorrect, as it suggests a negative consequence that is inconsistent with the argument's emphasis on the benefits of employee training.</o>"}	2
CR	<biological_sciences> - <CR> - <find the assumption> - <difficulty_level: 4>	844	4	2	Assumption about Gut Microbiomes and Mental Health	Which of the following is an assumption made by the argument regarding the relationship between gut microbiomes and mental health disorders?	4	0	0	{"passages": ["Recent studies in biological sciences suggest that exposure to certain environmental factors can significantly influence gene expression. These findings imply that lifestyle choices, such as diet and exercise, may play a crucial role in determining an individual's health outcomes. However, critics argue that the data is not yet conclusive enough to draw definitive conclusions about the long-term effects of these factors on genetic predispositions. To fully understand the relationship between environment and genetics, further research is necessary.", "A recent breakthrough in biological sciences has shown that certain microbiomes in the human gut can significantly affect mental health. Researchers claim that this discovery could lead to new treatments for mental health disorders by manipulating gut bacteria. However, the efficacy of such treatments is still under debate. Critics point out that the correlation between gut microbiomes and mental health does not necessarily imply causation. Thus, further studies are required to establish a more reliable link and potential treatment pathways."]}	2025-02-09 03:33:01.366	2025-02-09 03:33:01.366	f	\N	46	t	{"solution": "<br>The correct answer is A: Manipulating gut bacteria can lead to mental health improvements.<br>This is the key assumption in the argument, as it suggests that the proposed treatment can have a positive effect on mental health outcomes based on the correlation observed.<br><o>Option B is incorrect because while microbiomes may influence mental health, they are not necessarily the only factor involved; other biological and environmental factors could also play a role.</o><br><o>Option C is incorrect because not all gut bacteria have the same effect on mental health; different strains may vary in their impact.</o><br><o>Option D is incorrect as the argument specifically explores the relationship between gut microbiomes and mental health, suggesting that other factors, including lifestyle and environmental influences, can also contribute to mental health disorders.</o><br><o>Option E is incorrect because the argument does not assert that current treatments are ineffective, only implying that there could be new avenues of treatment based on gut bacteria manipulation.</o>"}	9
CR	<literature> - <CR> - <evaluate the conclusion> - <difficulty_level: 4>	838	4	2	Evaluating the Conclusion on Technology-Themed Novels	In the passage, the author concludes that while technology-themed novels act as cautionary tales, they may foster a simplistic view of the technological landscape. Which of the following best evaluates the author’s conclusion?	4	0	0	{"passages": ["In recent years, there has been a significant increase in the number of novels incorporating themes of technology and its impact on society. Scholars argue that these novels not only reflect contemporary anxieties about technological advancements but also shape readers' perceptions of these changes. For instance, the novel 'Digital Shadows' presents a dystopian future where technology drives society to the brink of chaos, highlighting potential consequences of unregulated tech growth. Critics, however, have noted that while such narratives raise valid concerns, they often overlook the benefits technology brings, such as improved communication and access to information. Thus, one can conclude that while technology-themed novels serve as valuable cautionary tales, they may also foster a simplistic view of the technological landscape.", "Literary critics have long debated the role of the author in interpreting a text. In his latest work, acclaimed author James P. Roberts contends that understanding a text requires considering the author's intent, arguing that readers who disregard this often misinterpret the work. He cites examples from his own novels, where the underlying themes significantly change depending on the reader's awareness of his personal experiences and societal context. However, some critics argue that overemphasizing authorial intent restricts the interpretive freedom of readers. They suggest that meaning is co-created by the reader and the text, independent of the author's background. Ultimately, while Roberts presents a compelling argument, one must evaluate whether his conclusion properly accounts for the vast array of interpretations that literature allows."]}	2025-02-09 03:33:01.294	2025-02-09 03:33:01.294	f	\N	46	t	{"solution": "The best evaluation of the author's conclusion is option A. <br> <o>The conclusion is well-supported as it acknowledges both the warnings and the limitations present in technology-themed literature.</o> <br> <o>This reflects the complexity of the issue and recognizes that while cautionary tales have merit, they may also lead to oversimplification.</o> <br> <o>Option B is incorrect because although literature evolves, the conclusion stands on its own merit regarding current works, regardless of future developments.</o> <br> <o>Option C is incorrect as it implies that the general audience may not always perceive both sides, which the author suggests is a risk.</o> <br> <o>Option D is not a valid critique since the passage does not lack examples; it is focused on the broader conclusion from the discussion.</o> <br> <o>Option E presents a viewpoint but lacks depth, as it does not address the complexities raised in the passage regarding the authors' perspectives.</o>"}	3
CR	<business> - <CR> - <complete the argument> - <difficulty_level: 2>	839	4	2	Completing the Argument on Remote Work Benefits	Based on the passage, which of the following best completes the argument: 'Thus, businesses that implement remote work policies will likely not only improve productivity but also...' 	2	0	0	{"passages": ["In recent years, many tech companies have shifted their focus from hardware production to software development. This transformation is mainly driven by the increasing demand for innovative software solutions that help businesses operate more efficiently. As a result, companies that have adapted to this trend are experiencing substantial growth. Therefore, if tech companies continue to prioritize software development, they are likely to maintain their competitive edge in the market.", "The introduction of remote work policies has led to significant changes in employee productivity. Businesses that embraced these policies reported an increase in overall productivity levels. Furthermore, employees indicated higher job satisfaction due to the flexibility that remote work offers. Therefore, it can be concluded that adopting remote work policies not only enhances productivity but also contributes to better employee morale, leading to a more committed workforce."]}	2025-02-09 03:33:01.308	2025-02-09 03:33:01.308	f	\N	46	t	{"solution": "The correct answer is A: foster a more engaged and loyal workforce.<br> This option logically follows the argument presented in the passage, as it emphasizes the connection between remote work policies, productivity, and employee morale, suggesting that a satisfied workforce is more likely to be engaged and loyal.<br><o>Option B, reduce the need for office space altogether, while potentially true, is not a direct continuation of the argument regarding productivity and morale.</o><br><o>Option C, eliminate the challenges of team collaboration, contradicts the idea that remote work may introduce new communication challenges.</o><br><o>Option D, increase operational costs in the long term, goes against the positive outcomes suggested in the passage.</o><br><o>Option E, create confusion among employees regarding their roles, is inconsistent with the premise that remote work leads to higher job satisfaction and engagement.</o>"}	4
CR	<psychology> - <CR> - <evaluate the conclusion> - <difficulty_level: 2>	840	4	2	Evaluating the Conclusion on Creativity and Happiness	What can be concluded from the survey indicating that people who engage in creative activities report higher happiness levels, given that the survey does not account for factors like social relationships or physical health?	2	0	0	{"passages": ["Recent studies in psychology suggest that individuals who practice mindfulness techniques tend to experience lower levels of stress. This finding implies that a routine incorporation of mindfulness practices into daily life could enhance overall mental well-being. As more people adopt these techniques, it is reasonable to expect a general improvement in societal mental health metrics. However, further research is necessary to explore the long-term effects of these practices on diverse populations.", "A recent survey indicates that people who regularly engage in creative activities, such as painting or writing, report feeling happier compared to those who do not. This suggests a potential link between creativity and increased happiness. Many psychologists propose that engaging in creative activities allows individuals to express their emotions, which can contribute to a greater sense of fulfillment. Nevertheless, the survey does not account for other factors that may influence happiness, such as social relationships or physical health."]}	2025-02-09 03:33:01.32	2025-02-09 03:33:01.32	f	\N	46	t	{"solution": "The correct answer is C: There may be other unconsidered factors that contribute to the reported happiness of individuals engaged in creative activities.<br> <o> This option appropriately acknowledges that the survey does not account for various other influences on happiness, which is crucial when evaluating the conclusion drawn from the survey.</o><br> <o> <strong>Option A</strong> is incorrect because it presents an absolute statement that does not consider the nuances involved; creativity does not guarantee happiness for everyone.</o><br> <o> <strong>Option B</strong> is incorrect as it claims the survey provides conclusive evidence without recognizing the limitations mentioned, such as other contributing factors.</o><br> <o> <strong>Option D</strong> is incorrect because it makes a generalization about less happy individuals, which cannot be inferred directly from the survey results.</o><br> <o> <strong>Option E</strong> is also incorrect, as it ignores the possibility that social relationships and physical health could interact with the level of creative activity to affect happiness.</o>"}	5
CR	<literature> - <CR> - <structure of the argument dialogue structure question> - <difficulty_level: 4>	841	4	2	Identifying the Role of a Statement in a Dialogue on Literature Curriculum	In the exchange between Professor Adams and Dr. Lee, which of the following best describes the role of Dr. Lee's statement: 'It's important to balance the curriculum by including diverse authors whose works reflect the varied experiences of today’s society.'?	4	0	0	{"passages": ["In a recent debate about the relevance of classic literature in modern education, two prominent educators presented their views. Dr. Smith argued that classic literature provides foundational knowledge that shapes critical thinking and cultural literacy in students. She noted, 'Understanding the historical context of these works enables students to grasp complex societal issues in today’s world.' On the other hand, Mr. Johnson contended that the focus on classic texts often overlooks contemporary voices that can resonate more with today's students. He stated, 'While classic literature is important, we must also include current narratives that reflect the diverse experiences of our society.' The debate concluded with each educator acknowledging the merits of the other's perspective, yet they remained firm in their initial positions.", "During a panel discussion on integrating literature into the curriculum, Professor Adams emphasized the importance of classic works in developing analytical skills. He asserted, 'Classic literature presents enduring themes that challenge students to think critically and engage deeply with complex characters.' In contrast, Dr. Lee raised concerns about the lack of representation in classic texts, arguing, 'It's important to balance the curriculum by including diverse authors whose works reflect the varied experiences of today’s society.' Professor Adams responded by acknowledging Dr. Lee's point, stating, 'While I agree that diversity is crucial, we must not discard the classics that have shaped literary tradition.' This exchange highlighted the ongoing tension between maintaining tradition and embracing inclusivity in educational content."]}	2025-02-09 03:33:01.332	2025-02-09 03:33:01.332	f	\N	46	t	{"solution": "The correct answer is A: <br> Dr. Lee's statement serves as a counterargument to Professor Adams' assertion by highlighting the need for balance in the curriculum and advocating for the inclusion of diverse authors. <br> <o> B is incorrect because Dr. Lee does not support the emphasis on classic literature; instead, he advocates for more contemporary voices. <br> <o> C is incorrect because Dr. Lee's statement does not provide a historical perspective; it focuses on the need for diversity in the curriculum. <br> <o> D is incorrect because Dr. Lee’s statement does not summarize Professor Adams' argument; rather, it challenges it. <br> <o> E is incorrect as Dr. Lee's statement is directly related to the ongoing debate about the literature curriculum."}	6
CR	<history> - <CR> - <paradox> - <difficulty_level: 4>	842	4	2	Paradox of Ignored Innovators in History	What is the underlying paradox presented in the passage regarding historical figures and their contributions to knowledge?	4	0	0	{"passages": ["Throughout history, many empires have risen to great heights, only to ultimately collapse. The Roman Empire, for instance, was once the epitome of strength and governance, commanding vast territories and a prosperous economy. However, it eventually fell into disrepair despite having an organized military and a sophisticated political structure. In contrast, some smaller, less organized societies have persisted for centuries, adapting to their environments without grand military campaigns or extensive bureaucracies. This disparity raises a paradox: why do some seemingly weaker societies endure while powerful empires dissolve?", "In the quest for knowledge, many historical figures are celebrated for their groundbreaking discoveries, yet paradoxically, some of the greatest contributions to science and philosophy came from those who were often dismissed or ignored. The works of individuals like Hypatia of Alexandria were overshadowed by the dominant male scholars of her time, yet her teachings influenced generations. Similarly, the ideas of early feminists like Mary Wollstonecraft were often met with ridicule, but they laid the groundwork for modern gender studies. This presents a paradox: why do revolutionary ideas sometimes emerge from the shadows, when society tends to favor established norms and accepted authorities?"]}	2025-02-09 03:33:01.344	2025-02-09 03:33:01.344	f	\N	46	t	{"solution": "The correct answer is <b>B</b>: Some significant ideas are developed by those who are overlooked or marginalized.<br> This choice accurately reflects the paradox presented in the passage, highlighting how influential contributions often arise from individuals who do not receive immediate recognition.<br><o>Option A</o> is incorrect because it suggests that strong contributions only come from recognized figures, which contradicts the passage's argument.<br><o>Option C</o> is inaccurate as the passage illustrates that revolutionary ideas may not be readily accepted; rather, they can be dismissed initially.<br><o>Option D</o> misrepresents the situation, as the passage shows that established scholars may belittle new theories instead of supporting them.<br><o>Option E</o> is also incorrect because the passage implies that cultural contexts do play a role in the reception of new ideas, especially in the case of marginalized figures."}	7
CR	<biological_sciences> - <CR> - <find the assumption> - <difficulty_level: 2>	843	4	2	Identify the assumption in the phage therapy argument for antibiotic resistance	What is the underlying assumption of the argument that phage therapy could be a viable solution for treating antibiotic-resistant bacteria?	2	0	0	{"passages": ["In the field of biological sciences, the recent advancements in genetic engineering have led to significant improvements in agricultural productivity. Researchers argue that by modifying the genetic material of crops, it is possible to create strains that are more resistant to pests and diseases, thereby reducing the need for chemical pesticides. These developments are seen as essential for feeding the growing global population. Despite the promising benefits, there are concerns about the long-term effects of genetically modified organisms (GMOs) on health and the environment. Supporters of genetic engineering contend that the potential benefits outweigh the risks, believing that rigorous testing and regulations can mitigate negative consequences.", "The increasing prevalence of antibiotic-resistant bacteria has raised alarms within the medical community and prompted researchers to investigate the use of alternative treatments. Some scientists hypothesize that phage therapy, which uses bacteriophages to target and kill specific bacteria, could be a viable solution. Proponents of phage therapy argue that it is more effective than traditional antibiotics and has fewer side effects. However, this approach assumes that phages can be easily isolated and characterized for therapeutic purposes. Additionally, there is an underlying assumption that the regulatory framework for new treatments will adapt to allow for the use of phage therapy in clinical settings."]}	2025-02-09 03:33:01.355	2025-02-09 03:33:01.355	f	\N	46	t	{"solution": "The correct answer is <b>A</b>: Phages can be effectively isolated and characterized for therapeutic use.<br> This is the underlying assumption of the argument since the viability of phage therapy hinges on the ability to isolate and properly use specific bacteriophages against antibiotic-resistant bacteria.<br><o>Option B</o>: Antibiotic-resistant bacteria are indeed a significant public health threat, but this statement is not an assumption; it is a widely accepted premise of the argument.<br><o>Option C</o>: There is no assumption made about the relative acceptance of phage therapy compared to traditional antibiotics within the passage.<br><o>Option D</o>: While phages may have fewer side effects than some antibiotics, the statement that they are safer than all existing antibiotics is not discussed as an assumption in the passage.<br><o>Option E</o>: Understanding the mechanisms of antibiotic resistance is important but does not relate to the assumption about the feasibility of phage therapy."}	8
DS	<linear inequalities>- <difficulty-level: 3>	845	1	1	Linear Inequalities and City Inhabitants with Pets	Based on the above statements, can we conclude that it is possible for the city to have at least 20 inhabitants with more than 5 pets?	3	0	0	{"passage": "In a peculiar city ruled by logic, the population of the city can be described by a linear inequality. Assume the number of inhabitants, x, satisfies the inequality 2x + 3y ≤ 100, where y represents the number of pets owned by the inhabitants. The mayor wants to determine whether it is possible for the city to have at least 20 inhabitants with more than 5 pets. Given this premise, we consider the following statements. ", "statements": ["The total number of inhabitants in the city is at least 30.", "Each inhabitant owns at least 3 pets."]}	2025-02-09 03:43:40.101	2025-02-09 03:43:40.101	f	\N	47	t	{"solution": "To determine if the statements are sufficient, we analyze each one. Statement (1) states that the total number of inhabitants is at least 30. This information alone does not indicate whether there can be 20 inhabitants with more than 5 pets. Statement (2) suggests that each inhabitant owns at least 3 pets. While this may help in assessing the pet ownership, it does not provide a direct link to the number of inhabitants having more than 5 pets. Both statements do not provide sufficient information independently or together, as we need to focus on the specific combinations of these numbers to conclude whether 20 inhabitants can have more than 5 pets. Therefore, the correct answer is E: Statements (1) and (2) TOGETHER are NOT sufficient."}	1
DS	<permutations and combinations>- <difficulty-level: 1>	846	1	1	Determining Actor Arrangements in a Theater Production	Based on the information above, can the total number of arrangements of actors into these 3 roles be determined?	1	0	0	{"passage": "In a local theater production, 5 actors are selected to play 3 leading roles. The roles are distinguished by the level of experience required: Role A needs 3 years of professional acting experience, Role B needs 2 years, and Role C requires at least 1 year. If each actor meets the experience criteria, how many different arrangements of actors are possible for these roles?", "statements": ["The total number of different actors available for selection is 7.", "The arrangement of roles is fixed, meaning each role is distinct and cannot be interchanged."]}	2025-02-09 03:43:40.12	2025-02-09 03:43:40.12	f	\N	47	t	{"solution": "To determine the total number of arrangements of actors into the distinct roles, we need to assess both statements. Statement (1) indicates that there are 7 actors available, but it does not specify how many meet the experience requirements, which leaves the arrangement undetermined. Statement (2) clarifies that each role is fixed and distinct, meaning we cannot interchange roles. However, this alone does not provide information on how many actors are qualified for the roles. Thus, both statements together do not provide sufficient information to calculate the arrangements, as we still lack details about the qualified actors. Hence, the correct answer is E: Statements (1) and (2) TOGETHER are NOT sufficient."}	2
DS	<Unitary method>- <difficulty-level: 1>	847	1	1	Bakery Revenue Analysis: Determining Danishes Income	Based on the statements above, can we determine the total revenue generated from danishes?	1	0	0	{"passage": "In a small town, a bakery sells two types of pastries: croissants and danishes. Last Saturday, the bakery sold a total of 150 pastries, and the number of croissants sold was twice the number of danishes sold. If the bakery's revenue from croissants was 3 times that from danishes, what was the revenue generated from danishes? ", "statements": ["The bakery sold 60 croissants.", "The bakery sold danishes at a price of $2 each."]}	2025-02-09 03:43:40.133	2025-02-09 03:43:40.133	f	\N	47	t	{"solution": "To determine the total revenue generated from danishes, we need to analyze the statements. From Statement 1, if the bakery sold 60 croissants and knowing that the number of croissants sold was twice the number of danishes, we can deduce that 30 danishes were sold. However, we do not have the price of danishes from this statement. Statement 2 provides the price of danishes as $2 each. With both statements, we can calculate the total revenue from danishes (30 danishes × $2 = $60). Since together the statements allow us to find the total revenue, the correct answer is C: BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient."}	3
NE	<mean median mode>- <difficulty-level: 1>	848	1	1	Calculating the Mean and Median of Snacks Brought by Friends	A group of seven friends decided to have a picnic and brought a variety of snacks. The number of snacks each friend brought is as follows: 3, 5, 7, 2, 8, 4, and 6. What is the mean and median number of snacks brought by the friends?	1	0	0	{"answer": 5.0}	2025-02-09 03:43:40.149	2025-02-09 03:43:40.149	f	\N	47	t	{"solution": "<p>To find the mean, we sum the number of snacks: ~~3 + 5 + 7 + 2 + 8 + 4 + 6 = 35~~. We then divide by the number of friends: ~~35 / 7 = 5~~. <br> For the median, we first arrange the numbers in order: 2, 3, 4, 5, 6, 7, 8. Since the number of friends is odd, the median is the middle number, which is 5.</p>"}	4
DS	<number theorm>- <difficulty-level: 4>	849	1	1	Determining the Possible Value of Prime q in a Number Set	Based on the above statements, can we determine the possible value of q?	4	0	0	{"passage": "In a certain number set, the product of two prime numbers, p and q, results in a composite number n. The sum of the digits of n is 12. Additionally, if n is divided by p, the quotient is another prime number r. Given that p is less than 10, what is the possible value of q if it's known that the difference between p and q is a prime number?", "statements": ["The only possible values for p are 2, 3, 5, and 7.", "The sum of the digits of q is 5."]}	2025-02-09 03:43:40.153	2025-02-09 03:43:40.153	f	\N	47	t	{"solution": "To determine the possible value of q, we evaluate the statements. Statement (1) provides us with the possible values of p, which are all primes less than 10: 2, 3, 5, and 7. Statement (2) gives us that the sum of the digits of q is 5. However, neither statement alone can conclusively lead to a specific value of q. When combined, we can identify the possibilities more clearly. For instance, if p is 2, q could be a prime such as 3, as their difference (1) is not prime. Other combinations hold similarly but require thorough checking. Therefore, while the two statements together narrow down options, they still do not provide a definitive answer for q. Hence, the correct answer is E: Statements (1) and (2) TOGETHER are NOT sufficient."}	5
		866	1	1	Calculating Profit Margin for Product B After Loss and Discount Adjustments	From the second pivot table data for Product B, if the total sales revenue is \\$60,000, calculate the overall profit margin after deducting the loss and discount. What would be the new profit margin percentage derived from the given financial data?	1	0	0	{}	2025-02-09 03:43:40.388	2025-02-09 03:43:40.388	t	91	48	t	{"solution": "For Product B, the initial profit is $15,000. After accounting for a loss of $3,000 and applying a discount of 5% on the total sales revenue of $60,000, the adjusted profit is calculated as follows: \\\\( Adjusted Profit = Profit - Loss - Discount \\\\). Thus, \\\\( Adjusted Profit = 15000 - 3000 - (60000 \\\\times 0.05) = 9000 \\\\). This adjusted profit reflects a profit margin of 15% against the total sales revenue."}	9
MCQ-Multi	<number theorm>- <difficulty-level: 1> (multi-correct MCQ)	850	1	1	The Dance of Numbers: Arranging Even and Odd for the Festive Parade	In a peculiar land where numbers dance, a group of numbers is organizing a festive parade. Among them, there are 45 participants in total. The numbers follow a specific set of rules: each even number must always be followed by an odd number, while odd numbers can stand alone or be followed again by another odd number. If the even numbers chosen are 2, 4, 6, 8, 10, and the odd numbers are chosen from 1, 3, 5, 7, 9, how many valid arrangements of these numbers can be formed for the parade if exactly 5 even numbers and 5 odd numbers are to be used in the parade? Specify the arrangements that adhere to the mentioned rules, and it is important to determine which of the following statements may be true.	1	0	0	{}	2025-02-09 03:43:40.166	2025-02-09 03:43:40.166	f	\N	47	t	{"solution": "<p>To find the total number of valid arrangements of the parade, we recognize that we have 5 even numbers and 5 odd numbers to arrange. The arrangement must follow the rules where each even number is followed by an odd number, resulting in a sequence structure of E, O, E, O, E, O, E, O, E, O. <br> <br> The total number of arrangements can be computed by using the formula: <br> Total arrangements = (number of even numbers)! * (number of odd numbers)! <br> <br> Therefore, the calculations are as follows: <br> 1. Number of arrangements of the even numbers = 5! = 120. <br> 2. Number of arrangements of the odd numbers = 5! = 120. <br>  <br> The total arrangements = 120 * 120 = 14400.</p>"}	6
MCQ-Multi	<geometry>- <difficulty-level: 4> (multi-correct MCQ)	851	1	1	Determining Possible Values of x for Triangle Areas in a Unique Geometric Town	In a peculiar geometric town, there exists a triangular park where the lengths of the sides are represented by the expressions 3x + 5, 4x - 2, and 5x - 3. The park’s area is also a subject of curiosity, as it is demarcated by a walkway that forms another triangle inside, each side of which is given by the expressions (x + 2), (2x - 1), and (x + 3). The citizens of the town hold a contest to determine if it is possible for the area of the inner triangle to be equal to 24 square units, given specific conditions on x. What values of x could potentially fulfill this requirement, ensuring that both the side lengths of the outer triangle are valid and the area condition is satisfied? Analyze the side lengths and the area requirement for both triangles and conclude which values of x can be possible.	4	0	0	{}	2025-02-09 03:43:40.176	2025-02-09 03:43:40.176	f	\N	47	t	{"solution": "<p>To find the possible values of x, we start by analyzing the geometries of the triangles involved. The outer triangle's sides are given as follows: <br> 1st side: 3x + 5 <br> 2nd side: 4x - 2 <br> 3rd side: 5x - 3 <br><br> We first ensure these values are positive for valid side lengths: <br> 3x + 5 > 0, 4x - 2 > 0, and 5x - 3 > 0. By solving these inequalities, we would need to derive suitable bounds for x. <br><br> Next, we calculate the area of the inner triangle using Heron's formula. Given the side lengths: <br> (x + 2), (2x - 1), (x + 3), we set the semi-perimeter s_inner and calculate the area accordingly. <br> Setting the area of the inner triangle equal to 24, we have the equation: <br> area_inner = 24. <br> By solving the equation using the derived quadratic relationship, the values of x are found as: <br> x = `-1/((-1296 + 3*sqrt(186621))**(1/3)*(-1/2 - sqrt(3)*I/2)) - (-1296 + 3*sqrt(186621))**(1/3)*(-1/2 - sqrt(3)*I/2)/3`, `-(-1296 + 3*sqrt(186621))**(1/3)*(-1/2 + sqrt(3)*I/2)/3 - 1/((-1296 + 3*sqrt(186621))**(1/3)*(-1/2 + sqrt(3)*I/2))`, and `-(-1296 + 3*sqrt(186621))**(1/3)/3 - 1/(-1296 + 3*sqrt(186621))**(1/3)`.</p>"}	7
		852	1	1	Revenue Growth Analysis for Retail Channel in Q3	Based on the sales data from the pivot table contrasting marketing channels and sales quarters, if the total revenue from the Retail channel in Q2 increased by 10% in Q3, what would be the new revenue for the Retail channel in Q3? Additionally, how does this new figure compare to the Online channel's revenue for the same quarter?	1	0	0	{}	2025-02-09 03:43:40.189	2025-02-09 03:43:40.189	t	89	47	t	{"solution": "The revenue for the Retail channel in Q2 was \\\\$15000. With a 10% increase in Q3, the new revenue for the Retail channel is calculated as follows: \\\\$15000 * (1 + 0.10) = \\\\$16500. In comparison, the revenue for the Online channel in Q3 is \\\\$25000. Therefore, the new revenue for the Retail channel in Q3 is \\\\$16500, which is \\\\$8490 less than the Online channel's revenue for the same quarter."}	8
		853	1	1	Projected Revenue Growth for Electronics in Q1	Considering the sales data in the pivot table outlining product categories and their revenues in Q4, if the total revenue from Electronics is projected to grow by 20% in the next quarter, what will be the estimated revenue for Electronics in Q1 of the following year? Additionally, how does this estimated revenue align with the revenue figures of Clothing for Q4?	1	0	0	{}	2025-02-09 03:43:40.2	2025-02-09 03:43:40.2	t	89	47	t	{"solution": "The revenue for Electronics in Q4 is \\\\$50000. Projecting a growth of 20% into Q1 of the following year, the estimated revenue for Electronics can be calculated as follows: \\\\$50000 * (1 + 0.20) = \\\\$60000. In comparison, the revenue for Clothing in Q4 is \\\\$30000. Therefore, the estimated revenue for Electronics in Q1 is \\\\$60000, which is \\\\$30000 more than the Clothing revenue for Q4."}	8
		854	1	1	Prediction of Compliance Rate for a Government Policy with Ranking of 45	Based on the scatter plot illustrating the relationship between government policies ranking and compliance rates, if a government policy ranks 45, what would you predict the compliance rate to be in percentage? Please provide a detailed analysis to support your prediction.	1	0	0	{}	2025-02-09 03:43:40.211	2025-02-09 03:43:40.211	t	90	47	t	{"solution": "To predict the compliance rate for a government policy with a ranking of 45, a linear regression model was used. By fitting the model to the scatter plot data, the predicted compliance rate is approximately 41.59%. This prediction is based on the established relationship observed in the scatter plot, indicating that as government policy rankings approach this value, compliance rates are expected to cluster around 41.59%."}	9
		855	1	1	Estimation of Compliance Rate for a Government Policy with Ranking of 80	Considering the scatter plot depicting the relationship between government policies ranking and compliance rates, what would be the estimated compliance rate for a policy with a ranking of 80? Explain the reasoning behind your estimate by analyzing the data presented in the graph.	1	0	0	{}	2025-02-09 03:43:40.219	2025-02-09 03:43:40.219	t	90	47	t	{"solution": "To estimate the compliance rate for a government policy with a ranking of 80, the previously trained linear regression model was used. The prediction generated from the model indicates that the estimated compliance rate is approximately 38.31%. This estimate is derived from the trend observed in the scatter plot, suggesting that as the government policy ranking increases to 80, the corresponding compliance rates reflect a decrease to about 38.31%."}	9
		856	1	1	Anticipated Compliance Rate for a Government Policy with Ranking of 95	Referring to the scatter plot showing the relationship between government policies ranking and compliance rates, if a policy has a very high ranking of 95, what could be the anticipated compliance rate? Provide your analysis based on the data trends observed in the scatter plot.	1	0	0	{}	2025-02-09 03:43:40.226	2025-02-09 03:43:40.226	t	90	47	t	{"solution": "To anticipate the compliance rate for a government policy with a ranking of 95, the linear regression model was employed again. The prediction suggests that the expected compliance rate is approximately 36.90%. This prediction is informed by the observed trend in the scatter plot, indicating that high-ranking policies tend to correlate with lower compliance rates, thus leading to an anticipated compliance rate of about 36.90%."}	9
DS	<linear inequalities>- <difficulty-level: 2>	857	1	1	Environmental Regulations on Vehicle Quantities in a Hypothetical City	Is it possible to determine if there exists a valid number of bicycles based on the statements provided regarding their quantity in relation to the number of cars and the city regulations given the current number of cars is 20?	2	0	0	{"passage": "In a hypothetical city, the number of bicycles, denoted by B, and the number of cars, denoted by C, must satisfy certain inequalities due to environmental regulations. Specifically, the city mandates that the number of bicycles must be at least twice the number of cars, which can be expressed as B ≥ 2C. Additionally, it is known that the total number of vehicles (bicycles and cars) cannot exceed 100, leading to the inequality B + C ≤ 100. Suppose the current number of cars is 20. Based on these regulations, are there possible valid solutions for the number of bicycles?", "statements": ["The number of bicycles is at least 40.", "The number of bicycles cannot exceed 80."]}	2025-02-09 03:43:40.235	2025-02-09 03:43:40.235	f	\N	48	t	{"solution": "To determine if we can find a valid number of bicycles based on the provided statements, we analyze each statement in conjunction with the inequalities. The first statement states that the number of bicycles is at least 40, which satisfies the inequality B ≥ 2C when C is 20, leading to B ≥ 40. The second statement indicates that the number of bicycles cannot exceed 80. Thus, we rewrite the total vehicle constraint: B + C ≤ 100 becomes B + 20 ≤ 100, or B ≤ 80. Therefore, both statements together give us the range 40 ≤ B ≤ 80. Since both statements provide bounds that make B valid according to the inequalities, we conclude that both statements together are indeed sufficient to conclude that there exists a valid number of bicycles satisfying the conditions. Thus, the answer is C: BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient."}	1
NE	<speed, distance and time>- <difficulty-level: 4>	858	1	1	Total Distance Traveled by a Cosmic Courier During an Intergalactic Delivery	In a vibrant world where intergalactic delivery services thrive, a cosmic courier embarked on a journey to deliver packages across different planets. Initially, the courier sped through the Milky Way at a velocity of 120 kilometers per hour for the first 4 hours, covering a significant distance. However, upon sensing a space-time fluctuation, the courier was compelled to increase their speed by 25% for the ensuing 6 hours. Compounded by a detour that required an additional 50 kilometers to be covered, the courier faced a unique challenge. What is the total distance traveled by the courier during this mission, considering both the time and the detour?	4	0	0	{"answer": 1430.0}	2025-02-09 03:43:40.247	2025-02-09 03:43:40.247	f	\N	48	t	{"solution": "<p>Segment 1: Initial speed = 120 km/h <br> Time traveled = 4 hours <br> Distance covered = ~~120 km/h * 4 hours = 480 km~~ <br> Segment 2: Increased speed = 120 km/h * 1.25 = 150 km/h <br> Time traveled = 6 hours <br> Distance covered = ~~150 km/h * 6 hours = 900 km~~ <br> Additional detour distance = 50 km <br> Total distance traveled = ~~480 km + 900 km + 50 km = 1430 km~~ </p>"}	2
DS	<profit, loss and discount>- <difficulty-level: 4>	859	1	1	Evaluating Profit from Handbag Sales After Discounts and Buybacks	Is the total profit of the boutique sufficient to determine whether the sales strategy is effective?	4	0	0	{"passage": "A boutique sells three different types of handbags: A, B, and C. Handbag A sells for $80, Handbag B sells for $120, and Handbag C sells for $150. During a seasonal sale, the boutique offers a 20% discount on Handbag A and a 30% discount on Handbag B. After the discounts, the boutique buys Handbag C back at an additional 10% off the original price for a promotional event. If the boutique sold 10 bags of A, 5 bags of B, and bought 3 bags of C, what is the total profit made by the boutique after all sales and buybacks are accounted for?", "statements": ["Statement (1): The boutique has a fixed cost of $500 that needs to be included in the total profit calculation.", "Statement (2): The boutique's selling price after discounts for Handbag A and B can be calculated as $64 and $84, respectively."]}	2025-02-09 03:43:40.25	2025-02-09 03:43:40.25	f	\N	48	t	{"solution": "To determine whether the sales strategy is effective by analyzing the total profit, we need to assess if the information from the provided statements gives us enough insight. Statement (1) provides a fixed cost, which is necessary to calculate the total profit accurately. Statement (2) gives us the discounted selling prices for Handbags A and B. Both statements together allow us to compute the total profit by considering sales revenue from all handbags and subtracting costs, therefore they are sufficient in tandem. However, Statement (1) alone does not give us enough information since we still need the selling prices, and Statement (2) alone does not provide the fixed cost. Thus, the correct option is C: BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient."}	3
DS	<permutations and combinations>- <difficulty-level: 5>	860	1	1	Culinary Combinations: Unique Three-Course Meals Analysis	Based on the statements provided, is the information sufficient to determine the total number of unique three-course meals the chef can prepare?	5	0	0	{"passage": "In a prestigious culinary competition, a chef wants to prepare a unique three-course meal using six distinct ingredients: chicken, broccoli, cheese, pasta, garlic, and lemon. The chef has a specific rule that the main ingredient of the entree must differ from the ingredients used in the appetizer and dessert. The chef also wants to ensure that no ingredient is repeated across any of the courses. Given these conditions, how many different combinations of three-course meals can the chef create? To determine whether the given data is sufficient, consider the following statements.", "statements": ["The chef decides that chicken will always be the main ingredient of the entree.", "The chef is considering broccoli and cheese as possible ingredients for the appetizer."]}	2025-02-09 03:43:40.262	2025-02-09 03:43:40.262	f	\N	48	t	{"solution": "To solve the problem, we need to assess the sufficiency of the statements provided. Statement (1) specifies that chicken is the main ingredient for the entree; however, this does not eliminate any other ingredient choices for the appetizer or dessert, leaving us with the remaining five ingredients to choose from for the two other courses. Statement (2) adds that the chef is considering broccoli and cheese for the appetizer, which narrows down the options for the appetizer and maintains the six total ingredients. Thus, while these statements provide some restrictions, they do not provide enough information to calculate the exact number of three-course meals due to the variances in choosing the appetizer and dessert based on the restrictions. Therefore, both statements together give insights into ingredient choices but ultimately do not allow us to derive a definitive total count of unique combinations. Hence, the correct answer is E: Statements (1) and (2) TOGETHER are NOT sufficient."}	4
DS	<permutations and combinations>- <difficulty-level: 2>	861	1	1	Combination Exploration of Elements in Energy Production	How many distinct combinations can be formed with the elements discussed?	2	0	0	{"passage": "In a futuristic society, a group of scientists is trying to determine the different combinations of elements that can produce a new type of energy. They have 5 unique elements: A, B, C, D, and E. Each combination can include any number of these elements, provided they are distinct and should include at least 2 elements. The scientists are tasked to find out how many distinct combinations can be formed only using elements A, B, and C. The researchers also wonder if including element D would yield more unique combinations than including only A, B, and C.", "statements": ["The number of distinct combinations using only elements A, B, and C is 4.", "Including element D, the number of distinct combinations raises to 8."]}	2025-02-09 03:43:40.327	2025-02-09 03:43:40.327	f	\N	48	t	{"solution": "To determine whether the statements are sufficient for answering the question, we analyze them. Statement (1) indicates that there are 4 distinct combinations using only elements A, B, and C, which is sufficient to show at least some combinations exist but does not give a complete picture of combinations with D. Statement (2) states that including D raises the number of combinations to 8, which directly informs the possibility and gives us more clarity about the overall count. Therefore, we need both statements together to conclusively determine the distinct combinations including whether D makes a difference. Hence, the correct answer is C: BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient."}	5
MCQ-Multi	<work and time>- <difficulty-level: 5> (multi-correct MCQ)	862	1	1	The Enchanted Tower: A Collaborative Work Challenge of Wizards	In a fantastical world where wizards and magical creatures coexist, a group of apprentices decides to build a magical tower. They have hired two wizards, Wizard A and Wizard B, to construct it. Wizard A can complete the tower alone in 12 hours, while Wizard B can do it in 15 hours. In their excitement, they decide to work together for the first 4 hours. After that, Wizard A, feeling fatigued, takes a break while Wizard B continues to work for another 4 hours alone. At this point, the apprentices realize they need to keep track of the tower's progress. They calculate the remaining work needed to finish the tower. However, unbeknownst to them, both wizards have enchanted the materials of the tower such that every hour they work causes the amount of work remaining to decrease by only 75% of the usual progress due to unpredictable magical resonances. After Wizard A re-joins Wizard B, they continue to finish the tower together. What fraction of the tower do they complete by the end of the 12th hour of working together? Which of the following statements about their work is true? 1) The total amount of work completed after 12 hours is less than 90%. 2) Wizard B, despite working more hours than Wizard A, contributed less to the overall construction due to magical interferences.	5	0	0	{}	2025-02-09 03:43:40.359	2025-02-09 03:43:40.359	f	\N	48	t	{"solution": "<p>Initially, Wizard A has a work rate of 1/12 of the tower per hour, and Wizard B has a work rate of 1/15 of the tower per hour.<br> In the first 4 hours working together, they produce: <br> Work done = (1/12 + 1/15) * 4 hours * 0.75 = 0.45 of the tower. <br> In the next 4 hours, Wizard B works alone: <br> Work done by B = (1/15) * 4 hours * 0.75 = 0.2 of the tower. <br> Total work done after 8 hours = 0.45 + 0.2 = 0.65 of the tower <br> Remaining work = 1 - 0.65 = 0.35 of the tower. <br> Finally, in the last 4 hours, both wizards work together again: <br> Work done = (1/12 + 1/15) * 4 hours * 0.75 = 0.45 of the tower. <br> Therefore, the final total work done = 0.65 + 0.45 = 1.1 of the tower.</p>"}	6
NE	<work and time>- <difficulty-level: 5>	863	1	1	Collaboration and Completion Time in a Sculpture Project	As part of a collaborative art project, a group of skilled artisans is tasked with creating a series of intricate sculptures. Artisan A can complete a sculpture by working 5 hours a day for 6 days, whereas Artisan B can finish the same sculpture in 8 hours a day over 4 days. After A and B work together for 2 days at their respective daily schedules, they find that Artisan C, who can create a sculpture in 12 hours a day over 3 days, joins them. What is the additional time Artisan C would need to complete the sculpture if Artisan A and Artisan B had produced a significant portion prior to C’s involvement?	5	0	0	{"answer": 6.0}	2025-02-09 03:43:40.367	2025-02-09 03:43:40.367	f	\N	48	t	{"solution": "<p>Artisan A can complete a sculpture in 30 hours (5 hours/day for 6 days). <br> Artisan B can complete a sculpture in 32 hours (8 hours/day for 4 days). <br> Over 2 days of work, Artisan A would complete ~~(5 hours * 2 days) / 30 hours = 1/3 sculpture~~, while Artisan B would complete ~~(8 hours * 2 days) / 32 hours = 1/2 sculpture~~. <br> Together, they've completed ~~1/3 + 1/2 = 5/6~~ of the sculpture. <br> This leaves ~~1 - 5/6 = 1/6~~ of the sculpture to complete. <br> Artisan C can finish a sculpture in 36 hours (12 hours/day for 3 days), giving Artisan C a rate of ~~1/36 sculptures per hour~~. <br> The additional time Artisan C needs to complete the remaining 1/6 of the sculpture is ~~(1/6) / (1/36) = 6 hours~~.</p>"}	7
MCQ-Multi	<work and time>- <difficulty-level: 4> (multi-correct MCQ)	864	1	1	The Gardener's Dilemma: How Efficiently Can Alice and Bob Plant Tulips?	In a peculiar town where the residents are obsessed with gardening, there are two gardeners, Alice and Bob, who are tasked with planting a flourishing Tulip garden. Alice can plant 120 Tulips in 6 hours, while Bob can plant 180 Tulips in 8 hours. The town’s council gives them an additional challenge: they must also arrange a further 240 Tulips into rows after planting them. They realize they can work together, boosting their efficiency by 25%. After working together for 4 hours, they are distracted by the town festival and take a 2-hour break. Upon returning, they find that due to their prolonged absence, the soil has dried up, causing the efficiency to drop by 50%. After accounting for the break and decreased efficiency, how many additional Tulips do Alice and Bob still need to plant to meet the requirement? How does their combined planting strategy affect their total time efficiency? Could their arrangements fulfill the requirement if they work a total of 10 hours?	4	0	0	{}	2025-02-09 03:43:40.37	2025-02-09 03:43:40.37	f	\N	48	t	{"solution": "<p>Alice's planting rate = 120 Tulips / 6 hours = 20 Tulips/hour <br> Bob's planting rate = 180 Tulips / 8 hours = 22.5 Tulips/hour <br> Combined planting rate = 20 + 22.5 = 42.5 Tulips/hour <br> With a 25% efficiency boost, the combined rate becomes = 42.5 * 1.25 = 53.125 Tulips/hour <br> In the first 4 hours of work, they plant = 53.125 * 4 = 212.5 Tulips.<br> After a 2-hour break due to the town festival, the remaining time is 10 - (4 + 2) = 4 hours. <br> However, their efficiency drops by 50%, leading to a decreased rate of = 53.125 * 0.5 = 26.5625 Tulips/hour.<br> Therefore, the Tulips they plant in the remaining 4 hours = 26.5625 * 4 = 106.25 Tulips.<br> Total Tulips planted = 212.5 + 106.25 = 318.75 Tulips.<br> Since they were assigned an additional task of arranging 240 Tulips, the remaining Tulips still needed to be planted = 240 - 318.75 = -78.75. Thus, they have planted 78.75 Tulips more than required.</p>"}	8
		865	1	1	Determining Adjusted Profit for Product A Based on Revenue, Losses, and Discounts	Given the financial data represented in the pivot table for Product A, if the total revenue was \\$50,000 in the first year, determine the percentage of profit after accounting for the losses and discounts applied. What would be the adjusted profit figure in comparison to the revenue?	1	0	0	{}	2025-02-09 03:43:40.38	2025-02-09 03:43:40.38	t	91	48	t	{"solution": "For Product A, the profit is $20,000. However, after accounting for a loss of $5,000 and applying a discount of 3% on the total revenue of $50,000, the adjusted profit is calculated as follows: \\\\( Adjusted Profit = Profit - Loss - Discount \\\\). Thus, \\\\( Adjusted Profit = 20000 - 5000 - (50000 \\\\times 0.03) = 13500 \\\\). This adjusted profit represents 27% of the total revenue."}	9
		867	1	1	Profit Margin Analysis for the Year 2015	In the year 2015, the company experienced a revenue of 600 million. If the annual expenses in the same year were 450 million, what was the profit margin in percentage for that year, and how does it compare to the profit margin in 2014?	1	0	0	{}	2025-02-09 03:43:40.399	2025-02-09 03:43:40.399	t	92	48	t	{"solution": "To find the profit margin for the year 2015, we first need to calculate the profit, which is the difference between revenue and expenses. The revenue in 2015 was 600 million and the expenses were 450 million. Thus, the profit is calculated as follows: \\n\\nProfit = Revenue - Expenses = 600 million - 450 million = 150 million.\\n\\nNext, the profit margin is calculated by dividing the profit by the revenue and multiplying by 100 to express it as a percentage:\\n\\nProfit Margin = (Profit / Revenue) * 100 = (150 million / 600 million) * 100 = 25%.\\n\\nNow, we compare it to the profit margin of 2014. The revenue for 2014 was 500 million, and if the expenses were 350 million:\\n\\nProfit for 2014 = 500 million - 350 million = 150 million.\\n\\nProfit Margin for 2014 = (150 million / 500 million) * 100 = 30%.\\n\\nTherefore, the profit margin for 2015 was 25%, which is a decrease compared to the profit margin of 30% in 2014."}	10
		868	1	1	Revenue Growth Percentage Analysis from 2014 to 2015	What was the total revenue growth percentage from 2014 to 2015, and how does this growth compare to the revenue growth from 2013 to 2014?	1	0	0	{}	2025-02-09 03:43:40.407	2025-02-09 03:43:40.407	t	92	48	t	{"solution": "To calculate the total revenue growth percentage from 2014 to 2015, we first need the revenue values for both years. We will use the following formula for revenue growth percentage:\\n\\nRevenue Growth Percentage = ((Revenue in Current Year - Revenue in Previous Year) / Revenue in Previous Year) * 100.\\n\\nFor the years in question:\\n- Revenue in 2015 = 600 million\\n- Revenue in 2014 = 500 million\\n\\nSo, the calculation for revenue growth from 2014 to 2015 is:\\n\\nRevenue Growth from 2014 to 2015 = ((600 - 500) / 500) * 100 = (100 / 500) * 100 = 20%.\\n\\nNext, we need to calculate the revenue growth from 2013 to 2014. For this, we must denote the revenue for 2013, which can be approximated from the previous data, assuming revenue in 2013 was 400 million:\\n\\n- Revenue in 2013 = 400 million\\n\\nThus, the growth percentage from 2013 to 2014 is:\\n\\nRevenue Growth from 2013 to 2014 = ((500 - 400) / 400) * 100 = (100 / 400) * 100 = 25%.\\n\\nIn summary, the total revenue growth percentage from 2014 to 2015 was 20%, which is less compared to the growth of 25% from 2013 to 2014."}	10
		869	1	1	Projected Allocation of AI Market Value in Retail and Healthcare Sectors	In 2025, the artificial intelligence market value is projected to reach 700 billion USD. If the retail sector utilizes 20% of this market value, what will be the dollar value allocation for AI applications in that sector? Additionally, how does this compare to the healthcare sector's allocation, which is indicated to obtain 25% of the market value?	1	0	0	{}	2025-02-09 03:43:40.418	2025-02-09 03:43:40.418	t	93	48	t	{"solution": "In 2025, the projected dollar allocation for AI applications in the retail sector is 140 billion USD, calculated by taking 20% of the total market value of 700 billion USD. In comparison, the healthcare sector is slated to receive 175 billion USD, obtained by applying the 25% allocation to the same total market value. This indicates that the healthcare sector will have a greater financial commitment to AI applications compared to the retail sector by 35 billion USD."}	11
		870	1	1	Financial Allocation of AI Applications in Finance, Healthcare, and Manufacturing Sectors	According to the pie chart, if the finance sector accounts for 35% of AI applications, how many billion USD does this translate to in 2025? Furthermore, if the combined allocation for the healthcare and manufacturing sectors is equal to the finance sector's allocation, what will be the dollar value for the manufacturing sector based on the information provided?	1	0	0	{}	2025-02-09 03:43:40.425	2025-02-09 03:43:40.425	t	93	48	t	{"solution": "In 2025, the dollar allocation for AI applications in the finance sector is approximately 245 billion USD, derived from 35% of the total market value of 700 billion USD. Furthermore, since the combined allocation for the healthcare sector (175 billion USD) and the manufacturing sector must equal the finance sector's allocation, the dollar value allocated for the manufacturing sector is approximately 70 billion USD."}	11
DS	<geometry>- <difficulty-level: 1>	871	1	1	Determining the Area of a Triangle with Side Lengths	Is the information provided in the statements sufficient to determine the area of the triangle?	1	0	0	{"passage": "In a certain triangle, the lengths of the two sides are represented as x and y, where x is double the length of y. The angle opposite to side y is 30 degrees. The area of the triangle can be calculated with the formula (1/2)*base*height. Can we determine the exact area of the triangle with this information?", "statements": ["Statement (1): The length of side y is 5 units.", "Statement (2): The length of side x is 10 units."]}	2025-02-09 03:43:40.433	2025-02-09 03:43:40.433	f	\N	48	t	{"solution": "Both statements provide the lengths of the sides of the triangle, with Statement (1) giving the length of side y as 5 units and Statement (2) giving the length of side x as 10 units. Using the formula for the area of a triangle, area = (1/2) * base * height, and with the angle of 30 degrees being given, we can calculate the height using trigonometric functions. Thus, both statements together provide sufficient information to calculate the area. However, either statement alone would not allow us to calculate the area since we need to know both side lengths to do so."}	12
TC-1	<Psychology> - <TC-1> - <difficulty-level: 2> - <vocabulary-level:1>	872	2	1	Cognitive Dissonance in Psychology	The concept of cognitive dissonance refers to the mental discomfort experienced when a person holds two or more contradictory beliefs, values, or ideas, leading to a state of _______ that motivates them to find consistency.	2	0	0	{}	2025-02-09 03:43:40.448	2025-02-09 03:43:40.448	f	\N	49	t	{"solution": "<p><strong>A</strong> is correct because cognitive dissonance inherently involves a state of confusion as individuals struggle to reconcile conflicting thoughts or beliefs.</p><hr/><p><strong>B</strong> is incorrect because clarity would imply a lack of dissonance.</p><hr/><p><strong>C</strong> is incorrect since excitement does not relate to the discomfort of conflicting beliefs.</p><hr/><p><strong>D</strong> is incorrect as apathy does not reflect the active mental struggle associated with cognitive dissonance.</p><hr/><p><strong>E</strong> is also incorrect; solitude is unrelated to the cognitive processes involved in dissonance.</p><hr/><p><strong>F</strong> is incorrect, as tranquility does not represent a state of dissonance but rather peace of mind.</p>"}	1
TC-2	<Philosophy> - <TC-2> - <difficulty-level: 3> - <vocabulary-level:2>	873	2	1	Philosophical Inquiry and Ethical Discussions	In the realm of philosophical inquiry, the distinction between _____ concepts and _____ ideas is often blurred, leading to confusion in ethical discussions.	3	0	0	{}	2025-02-09 03:43:40.464	2025-02-09 03:43:40.464	f	\N	49	t	{"solution": "<p>The correct options are <strong>A</strong> (abstract) and <strong>E</strong> (practical). In philosophical discourse, abstract concepts refer to those that are theoretical and cannot be directly observed, while practical ideas are grounded in real-world application. Thus, the interplay of these concepts often leads to ethical ambiguities.</p><hr/><p>Other options discussed:</p><ul><li><strong>B</strong> (concrete): This refers to tangible or specific items, which is generally the opposite of what is being explored here.</li><li><strong>C</strong> (substantial): Although related, it does not convey the nuanced distinction sought in ethical discussions.</li><li><strong>D</strong> (theoretical): While relevant, it does not pair as effectively with 'practical' as 'abstract' does.</li><li><strong>F</strong> (mythical): This is irrelevant to the discourse on philosophical concepts.</li><li><strong>G</strong> (empirical): This term refers to knowledge acquired through observation or experimentation, which doesn't fit the context of the philosophical debate here.</li><li><strong>H</strong> (speculative): While it touches on ideas that involve conjecture, it does not work well with 'abstract' to match the blank.</li></ul>"}	2
SE	<Psychology> - <SE> - <difficulty-level: 3> - <vocabulary-level:3>	874	2	1	Psychology of Decision-Making Under Pressure	The researcher found that the participants exhibited a ______ sense of urgency when faced with deadlines, which ultimately affected their decision-making process and task completion rates. This phenomenon often results in either a heightened __________ response to stress or a complete absence of motivation.	3	0	0	{}	2025-02-09 03:43:40.48	2025-02-09 03:43:40.48	f	\N	49	t	{"solution": "<p>The correct options are <b>A</b> and <b>F</b>. The sentence conveys that the sense of urgency can be viewed as either heightened or acute, thus indicating that participants respond more intensely under pressure.<br><br>Option A: <b>keen</b> is appropriate as it indicates a sharp and strong sense of urgency.<br>Option F: <b>acute</b> also indicates an intense and possibly overwhelming sense of urgency.<br><br>Other options:<br> - Option B: <b>dull</b> contradicts the idea of urgency.<br> - Option C: <b>neutral</b> does not reflect urgency at all.<br> - Option D: <b>overstated</b> suggests exaggeration, which does not fit the context.<br> - Option E: <b>irresolute</b> implies uncertainty and indecision, which contrasts with a sense of urgency.</p>"}	3
SE	<Politics> - <SE> - <difficulty-level: 5> - <vocabulary-level:1>	875	2	1	Politics: Election Results and Electorate Sentiments	The recent election results have created a sense of both _______ and _______ among the electorate, with many feeling hopeful about the future yet skeptical about the candidates' promises.	5	0	0	{}	2025-02-09 03:43:40.493	2025-02-09 03:43:40.493	f	\N	49	t	{"solution": "<p>The correct options are <strong>enthusiasm</strong> and <strong>cynicism</strong>, as they capture the duality of the electorate's feelings. On one hand, many voters may feel a sense of enthusiasm about potential positive changes, while on the other, there exists a strong current of cynicism regarding the candidates' commitments.</p><p>Here’s why the other options are less suitable:</p><ul><li><strong>Disappointment:</strong> This does not align with the hopeful sentiment implied in the question.</li><li><strong>Apathy:</strong> This suggests indifference, which is contrary to the notion of active feelings among the electorate.</li><li><strong>Optimism:</strong> This is similar to enthusiasm, but lacks the contrasting element of skepticism.</li><li><strong>Despair:</strong> This conveys a more negative sentiment than what is suggested by the juxtaposition of hope and skepticism.</li></ul>"}	4
TC-3	<Literature> - <TC-3> - <difficulty-level: 4> - <vocabulary-level:1>	876	2	1	Literature: The Duality of Heroism and Human Frailty in Tragedy	In his analysis of the classical tragedy, the author posits that the essence of such works lies not only in the ____ of heroic deeds but also in the profound ____ of human frailties and moral dilemmas, creating a narrative that resonates deeply with audiences. This duality serves to emphasize the tragic hero's eventual ____ and highlights the complexity of the human experience.	4	0	0	{}	2025-02-09 03:43:40.507	2025-02-09 03:43:40.507	f	\N	49	t	{"solution": "<p><strong>Option A:</strong> celebration - This fits the context as it captures the essence of heroic deeds, suggesting that the narrative highlights and honors these acts.</p><p><strong>Option F:</strong> revelation - This word conveys the deep understanding of human frailties and moral dilemmas, adding depth to the narrative.</p><p><strong>Option J:</strong> failure - This word accurately depicts the tragic hero's eventual downfall, aligning with the complexity of the human experience featured in classical tragedies.</p><p><strong>Other Options:</strong> <br> - B: recognition does not convey the sense of honor or celebration intended. <br> - C: abandonment does not relate to the context of heroic deeds. <br> - D: denial contradicts the analysis of human frailty. <br> - E: exaltation is too focused on elevated feelings, missing the deeper implications. <br> - G: exploration implies a journey without the tragic undertones. <br> - H: illustration is inadequate for conveying depth. <br> - K: ascendance implies success, which is inconsistent with tragedy. <br> - L: elevation does not link back to human frailties effectively.</p>"}	5
RC		877	2	1	Inference on Atmospheric Pressure and Weather Patterns	Based on the passages, which of the following statements can be inferred about the impact of atmospheric pressure on weather patterns?	4	0	0	{}	2025-02-09 03:43:40.531	2025-02-09 03:43:40.531	t	94	49	t	{"solution": "<p>The correct answer is <strong>C</strong>: Changes in atmospheric pressure can affect local ecosystems. This is supported by the notion that variations in atmospheric pressure lead to different weather conditions, which in turn influence ecosystems.</p><p><strong>A</strong>: High-pressure systems always lead to stormy weather is incorrect as high-pressure systems often result in clear, sunny conditions.</p><p><strong>B</strong>: Low-pressure zones are typically associated with clear weather is incorrect, as these areas are more commonly linked to cloud formation and precipitation.</p><p><strong>D</strong>: Understanding atmospheric pressure is irrelevant to weather predictions is also incorrect because knowledge of atmospheric pressure is crucial for making accurate weather forecasts.</p>"}	6
RC		878	2	1	Ethical Considerations in Genetic Engineering	What can be inferred about the ethical considerations surrounding genetic engineering based on the passage?	1	0	0	{}	2025-02-09 03:43:40.541	2025-02-09 03:43:40.541	t	94	49	t	{"solution": "<p>The correct answer is <strong>C</strong>: Ethical debates surrounding genetic modification highlight the need for responsible research. The passage indicates that the rapid advancements in genetic engineering have sparked discussions about ethics, implying that a consideration of responsibility is necessary.</p><p><strong>A</strong>: Genetic engineering poses no ethical concerns in agriculture is incorrect, as the passage suggests that ethical debates do exist in this field.</p><p><strong>B</strong>: There is a consensus among scientists that genetic engineering should proceed without regulation is incorrect, as the passage emphasizes the need for regulations to ensure responsible practices.</p><p><strong>D</strong>: The benefits of genetic engineering are universally agreed upon by all stakeholders is also incorrect, since the passage highlights ongoing debates about its ethical implications, suggesting that not all stakeholders agree on the benefits.</p>"}	6
RC		879	2	1	Assumptions of Quantum Entanglement in Computing and Cryptography	Which assumption underlies the assertion that quantum entanglement has implications for quantum computing and cryptography?	4	0	0	{}	2025-02-09 03:43:40.553	2025-02-09 03:43:40.553	t	94	49	t	{"solution": "<p>The correct answer is <strong>D</strong>: Utilizing quantum entanglement can enhance computational power and security. This assumption supports the assertion that quantum entanglement has significant implications for quantum computing and cryptography, suggesting that entangled particles can be harnessed for these advancements.</p><p><strong>A</strong>: Quantum entanglement only occurs in experimental settings is incorrect because entanglement can exist beyond the laboratory, influencing various applications.</p><p><strong>B</strong>: Entangled particles can communicate information faster than light is misleading. While entanglement shows correlations, it does not allow for faster-than-light communication, which would violate relativistic principles.</p><p><strong>C</strong>: The principles of classical physics can fully explain quantum mechanics is also incorrect, as quantum mechanics fundamentally differs from classical physics and often challenges its principles.</p>"}	6
RC		880	2	1	Understanding Economic Policy Frameworks	What is the main idea presented in the passages regarding the role of monetary and fiscal policy in the economy?	2	0	0	{}	2025-02-09 03:43:40.569	2025-02-09 03:43:40.569	t	95	49	t	{"solution": "<p>The correct answer is <strong>B</strong>: Both policies aim to balance immediate economic needs with long-term stability.</p> <p>This option accurately reflects the overarching theme of the passages, which discuss the importance of both monetary and fiscal policies in managing economic performance and stability. The passages illustrate how these policies interact to address immediate economic challenges while considering long-term implications for the economy.</p> <p><strong>A</strong> is incorrect because it dismisses the effectiveness of both policies, which have been shown to impact economic stability significantly.</p> <p><strong>C</strong> is incorrect as it neglects the role of monetary policy, which is discussed as crucial for influencing economic conditions.</p> <p><strong>D</strong> is incorrect because the passages clearly mention that monetary policy does indeed have a significant impact on employment levels and overall economic conditions.</p>"}	7
RC		881	2	1	Future Trends in Economic Policymaking	Based on the passages, which inference can be drawn about the future direction of economic policymaking?	5	0	0	{}	2025-02-09 03:43:40.579	2025-02-09 03:43:40.579	t	95	49	t	{"solution": "<p>The correct answer is <strong>B</strong>: Policymakers will need to integrate behavioral insights to address modern economic issues.</p> <p>This option is supported by the passages' discussion on the evolving landscape of economic policymaking, especially with the rise of behavioral economics and the need to account for cognitive biases and emotional responses in decision-making.</p> <p><strong>A</strong> is incorrect because the passages suggest that economic policymaking is adapting and evolving, particularly with the integration of behavioral insights.</p> <p><strong>C</strong> is incorrect as it does not reflect the comprehensive view of trade policy presented in the passages, which highlight the complexities involved rather than a singular focus on protective measures.</p> <p><strong>D</strong> is incorrect because the passages emphasize the relevance of both fiscal and monetary policies, suggesting they will continue to play vital roles in economic management.</p>"}	7
RC		882	2	1	Assumptions in Behavioral Economic Policymaking	What assumption underlies the argument that behavioral insights can improve economic policymaking?	5	0	0	{}	2025-02-09 03:43:40.589	2025-02-09 03:43:40.589	t	95	49	t	{"solution": "<p>The correct answer is <strong>B</strong>: Policies based on behavioral insights can lead to more effective economic outcomes.</p> <p>This assumption is central to the argument presented in the passages, which highlight that incorporating behavioral insights into policymaking could better align with actual human behavior, potentially resulting in improved economic outcomes.</p> <p><strong>A</strong> is incorrect because the argument specifically challenges the notion that individuals always make rational decisions, which is a key point in advocating for behavioral economics.</p> <p><strong>C</strong> is incorrect as the passages indicate that traditional economic models often fall short in accounting for actual human behavior, thereby necessitating the integration of behavioral insights.</p> <p><strong>D</strong> is incorrect because the argument made in the passages focuses on the role of government intervention as an important mechanism to achieve desired economic behaviors, especially in the context of addressing market failures.</p>"}	7
RC		883	2	1	Central Thesis on Economic Policy Interaction	What is the central thesis presented in the passages regarding the interaction of various economic policies?	1	0	0	{}	2025-02-09 03:43:40.598	2025-02-09 03:43:40.598	t	95	49	t	{"solution": "<p>The correct answer is <strong>B</strong>: The synergy between monetary and fiscal policies is essential for economic stability.</p> <p>This reflects the central thesis of the passages, which discuss how both monetary and fiscal policies interact to manage economic performance and ensure stability within the economy.</p> <p><strong>A</strong> is incorrect because the passages emphasize the interconnectedness of various economic policies, rather than their independence.</p> <p><strong>C</strong> is incorrect as the passages highlight that global economic factors do significantly influence national policies, particularly in the context of trade and monetary frameworks.</p> <p><strong>D</strong> is incorrect because the passages assert that behavioral insights are increasingly relevant in shaping effective economic policies, particularly as they relate to human decision-making.</p>"}	7
TC-1	<Psychology> - <TC-1> - <difficulty-level: 4> - <vocabulary-level:2>	884	2	1	Psychology of Cognitive Dissonance	Despite extensive research into the concept of cognitive dissonance, the phenomenon remains ________, leaving researchers to grapple with its implications in behavioral psychology.	4	0	0	{}	2025-02-09 03:43:40.609	2025-02-09 03:43:40.609	f	\N	50	t	{"solution": "<p>The correct option is <b>A</b> (enigmatic), as it implies that the phenomenon of cognitive dissonance is mysterious and not fully understood, which aligns with the context of the question. The other options do not fit well because:</p><ul><li><b>B</b> (uncontested) suggests that there is no debate about it, which contradicts the notion of researchers grappling with it.</li><li><b>C</b> (trivial) downplays the significance of cognitive dissonance, which is not appropriate given its importance in psychology.</li><li><b>D</b> (ordinary) implies a lack of complexity or interest, which misrepresents the intriguing nature of the phenomenon.</li><li><b>E</b> (simple) also fails to capture the depth of discussion surrounding cognitive dissonance.</li><li><b>F</b> (resolute) implies firmness or a lack of ambiguity, which does not align with the intention of the statement.</li></ul>"}	1
TC-2	<Economics> - <TC-2> - <difficulty-level: 1> - <vocabulary-level:1>	885	2	1	Economic Stimulus and Inflation Management	In times of economic crisis, governments may implement stimulus measures to __________ spending and encourage economic growth, while simultaneously aiming to __________ inflationary pressures that could arise.	1	0	0	{}	2025-02-09 03:43:40.623	2025-02-09 03:43:40.623	f	\N	50	t	{"solution": "<p>In this context, the correct answers are <strong>augment</strong> and <strong>mitigate</strong>.<br><br> - <strong>augment</strong> (Option D) fits well as it means to increase or enhance spending, which is the purpose of stimulus measures.<br> - <strong>mitigate</strong> (Option F) is appropriate as it means to lessen or reduce inflationary pressures.</p><p>Other options for clarification:</p><ul><li><strong>dwindle</strong> (Option A) suggests a decrease in spending, which contradicts the intended purpose of stimulus measures.</li><li><strong>curtail</strong> (Option B) also implies a reduction in spending, which is not consistent with the goal of stimulating the economy.</li><li><strong>incite</strong> (Option C) suggests provoking or urging spending, rather than facilitating it.</li><li><strong>augment</strong> (Option D) was correctly chosen to reflect increasing spending.</li><li><strong>escalate</strong> (Option G) implies an increase that may not specifically relate to desirable inflation management.</li><li><strong>exacerbate</strong> (Option H) means to make a situation worse, which is contrary to mitigating inflation.</li></ul>"}	2
TC-1	<Literature> - <TC-1> - <difficulty-level: 1> - <vocabulary-level:1>	886	2	1	Literature: The Protagonist's Journey	In the novel, the protagonist's journey is marked by a series of _______ events that challenge her understanding of morality.	1	0	0	{}	2025-02-09 03:43:40.641	2025-02-09 03:43:40.641	f	\N	50	t	{"solution": "<p>The correct answer is <strong>C</strong> (anomalous) because the term suggests events that are unusual or out of the ordinary, effectively challenging the protagonist's understanding of morality as intended in the context of the sentence.</p><p><strong>Other Options:</strong></p><ul><li><strong>A</strong> (conventional): Implies events that are standard and typical, which would not present a challenge to her understanding.</li><li><strong>B</strong> (mundane): Suggests ordinary events that do not evoke any moral questioning.</li><li><strong>D</strong> (predictable): Indicates events that are expected and therefore would not challenge her perspective.</li><li><strong>E</strong> (benign): Refers to harmless events, again failing to provoke moral contemplation.</li><li><strong>F</strong> (trivial): Denotes events of little significance, which would not impact her understanding of morality.</li></ul>"}	3
TC-3	<Literature> - <TC-3> - <difficulty-level: 1> - <vocabulary-level:2>	887	2	1	Literary Complexity and Human Experience	In the realm of literature, a profound understanding of the human experience often hinges on an author's ability to create _______ characters, as they provide insight into the complex emotions we all _______ at various stages of life, ultimately reflecting the _______ of our own journeys.	1	0	0	{}	2025-02-09 03:43:40.657	2025-02-09 03:43:40.657	f	\N	50	t	{"solution": "<p>In this question, the correct answer is <strong>B</strong>, <strong>F</strong>, and <strong>J</strong>. This selection creates a coherent narrative about literature's ability to connect with human emotions.</p> <p><strong>B</strong> (multidimensional) best describes characters that resonate deeply with readers as they embody complexity. </p> <p><strong>F</strong> (experience) emphasizes that these characters reflect emotions that individuals actively engage with throughout their lives. </p> <p><strong>J</strong> (richness) concludes the thought by highlighting that the profound narratives shape our understanding of life's multifaceted journeys.</p> <p> <strong>Discussions on other options:</strong></p> <ul><li><strong>A</strong> (stereotypical) is incorrect as it implies a lack of depth.</li><li><strong>C</strong> (superficial) suggests that the characters offer little emotional insight.</li><li><strong>D</strong> (ordinary) doesn't capture the essence of impactful literary characters.</li><li><strong>E</strong> (ignore), <strong>G</strong> (observe), and <strong>H</strong> (forget) don't appropriately position the reader's relationship with these characters.</li><li><strong>K</strong> (triviality) and <strong>L</strong> (hollowness) contradict the idea of literary depth and richness.</li></ul>"}	4
SE	<Philosophy> - <SE> - <difficulty-level: 2> - <vocabulary-level:1>	888	2	1	Philosophy of Knowledge and Belief	In philosophical discourse, the concepts of knowledge and belief are often seen as _______ yet distinct elements, both serving critical roles in the formation of human understanding.	2	0	0	{}	2025-02-09 03:43:40.68	2025-02-09 03:43:40.68	f	\N	50	t	{"solution": "<p><b>Option A:</b> 'intertwined' suggests that knowledge and belief are closely connected yet different, which fits the context of their relationship.</p><p><b>Option E:</b> 'complementary' also works, indicating that knowledge and belief enhance each other in forming understanding.</p><p><b>Option B:</b> 'independent' fails as it implies separation without interaction, which contradicts the intended meaning.</p><p><b>Option C:</b> 'similar' does not capture the nuance between knowledge and belief, and thus is too simplistic.</p><p><b>Option D:</b> 'contradictory' directly opposes the idea of them being distinct but related.</p><p><b>Option F:</b> 'irrelevant' suggests a complete lack of connection, which is not accurate in philosophical discussions.</p>"}	5
TC-3	<Economics> - <TC-3> - <difficulty-level: 1> - <vocabulary-level:2>	889	2	1	Economic Policies and Cultural Influence	In considering the economic policies of various countries, it becomes clear that while some nations prioritize _______ (1), others are more focused on _______ (2) and _______ (3). These differences often stem from historical contexts and cultural influences that shape their respective goals.	1	0	0	{}	2025-02-09 03:43:40.693	2025-02-09 03:43:40.693	f	\N	50	t	{"solution": "<p>The correct answers are <b>protectionism</b> (B), <b>growth</b> (E), and <b>regulation</b> (I). Each of these terms reflects important facets of economic policies that countries may prioritize. </p><p>Option Discussion:</p><ul><li><b>Protectionism</b>: This indicates a focus on safeguarding local industries, making it a common priority for some nations.</li><li><b>Growth</b>: This underscores the importance of fostering economic expansion and development.</li><li><b>Regulation</b>: It signifies a nation’s approach to maintaining oversight on industries, often viewed as a cornerstone of managing economic activities.</li></ul><p>Other options do not fit as well:</p><ul><li><b>Liberation</b> (A): While vital, it does not fit the broader context of governmental policy focus.</li><li><b>Innovation</b> (C): Though crucial, it's often a means to achieve other ends rather than a primary focus.</li><li><b>Stability</b> (D): Important, but less often prioritized in competitive economic frameworks.</li><li><b>Inequality</b> (F): Typically, it is a concern that arises when discussing outcomes of economic policies rather than a goal.</li><li><b>Efficiency</b> (G): Focused on optimization, but not a direct policy goal.</li><li><b>Redistribution</b> (H): This usually stems from choices made related to inequality and is not a primary focus.</li><li><b>Intervention</b> (J): While significant, it is often seen as a reactive rather than proactive policy.</li><li><b>Reduction</b> (K): Vague without corresponding context.</li><li><b>Development</b> (L): Similar to growth but lacks specificity regarding economic policy goals.</li></ul>"}	6
RC		890	2	1	The Interdisciplinary Influence on Philosophical Understanding	How does the interdisciplinary approach in contemporary philosophy enhance the understanding of practical dilemmas?	4	0	0	{}	2025-02-09 03:43:40.716	2025-02-09 03:43:40.716	t	96	50	t	{"solution": "<p>The correct answer is <strong>B</strong>: It provides diverse perspectives that lead to more holistic solutions. This option highlights the importance of integrating various fields into philosophical inquiry, emphasizing that real-world dilemmas benefit from multiple viewpoints.</p><p><strong>A</strong>: It simplifies complex issues by removing philosophical jargon. This option is incorrect because effective interdisciplinary approaches don't necessarily simplify issues but rather deepen understanding through complexity.</p><p><strong>C</strong>: It promotes the idea that all philosophical problems have a definitive answer. This statement is misleading, as philosophy often thrives on the exploration of questions without absolute answers.</p><p><strong>D</strong>: It encourages philosophers to solely focus on abstract theories. This option is incorrect, as contemporary philosophy is increasingly about applying theoretical insights to practical situations, rather than distancing itself from practical concerns.</p>"}	7
RC		891	2	1	Implications of Neuroscience on Free Will	What can be inferred about the implications of neuroscience on the concept of free will as discussed in the passage?	3	0	0	{}	2025-02-09 03:43:40.726	2025-02-09 03:43:40.726	t	96	50	t	{"solution": "<p>The correct answer is <strong>B</strong>: The findings of neuroscience challenge traditional notions of autonomy. This reflects the passage's indication that new data on decision-making processes affects how free will is understood, suggesting a reevaluation of autonomy.</p><p><strong>A</strong>: Neuroscience definitively proves that humans lack free will. This option is incorrect because the passage does not assert a definitive conclusion but rather raises questions about the nature of free will.</p><p><strong>C</strong>: Philosophical discussions about free will are becoming irrelevant due to neuroscience. This is incorrect as the passage emphasizes the ongoing dialogue and importance of philosophical inquiry in light of scientific findings.</p><p><strong>D</strong>: Neuroscience supports the idea that all decisions are made consciously. This option is wrong since the passage suggests that brain activity can occur before conscious awareness, indicating that not all decisions are made with conscious intent.</p>"}	7
RC		892	2	1	Assuming Influence: The Legacy of the Renaissance	What assumption underlies the argument that the Renaissance significantly influenced modern societal structures?	1	0	0	{}	2025-02-09 03:43:40.738	2025-02-09 03:43:40.738	t	97	50	t	{"solution": "<p>The correct answer is <strong>B</strong>: The advancements made during the Renaissance had lasting effects on various aspects of society. This option accurately reflects the central assumption that the innovations and ideas of the Renaissance period have influenced subsequent societal developments.</p><p><strong>A</strong> is incorrect because while some Renaissance artists depicted religious themes, many also explored humanism and secular subjects, which indicates a broader range of influence.</p><p><strong>C</strong> is incorrect as it suggests that the Renaissance did not interact with the political changes of the time, which is false; in fact, it was deeply intertwined with various political transformations.</p><p><strong>D</strong> is incorrect since the Renaissance led to improved literacy rates, particularly due to the invention of the printing press, which made books more accessible.</p>"}	8
RC		893	2	1	Urbanization's Impact: Lessons from the Industrial Revolution	What can be inferred about the role of urbanization during the Industrial Revolution based on the passage?	3	0	0	{}	2025-02-09 03:43:40.748	2025-02-09 03:43:40.748	t	97	50	t	{"solution": "<p>The correct answer is <strong>C</strong>: Urbanization was a response to the demand for labor in factories. This inference aligns with the passage, which indicates that people moved to cities in search of work due to the establishment of factories during the Industrial Revolution.</p><p><strong>A</strong> is incorrect because the passage does not suggest that urbanization led to improvements in rural living conditions; rather, it highlights urban migration.</p><p><strong>B</strong> is incorrect as the passage clearly states that urbanization emerged as a result of factory labor demands, indicating a significant change in population distribution.</p><p><strong>D</strong> is incorrect since the Industrial Revolution caused notable demographic changes as people migrated to urban areas for employment opportunities.</p>"}	8
RC		894	2	1	Outcomes Assumed: The Consequences of the American Revolution	What assumption can be made about the outcomes of the American Revolution based on the passage?	2	0	0	{}	2025-02-09 03:43:40.757	2025-02-09 03:43:40.757	t	97	50	t	{"solution": "<p>The correct answer is <strong>A</strong>: The American colonies were unified in their desire for independence. This assumption is inferred from the passage, which discusses the collective quest for independence articulated in the Declaration of Independence.</p><p><strong>B</strong> is incorrect because the passage states that the revolution inspired various other nations, suggesting broader societal benefits beyond just the elite class.</p><p><strong>C</strong> is incorrect since the passage implies that the principles of equality and individual rights were not universally accepted before the revolution, making the assumption flawed.</p><p><strong>D</strong> is incorrect as the passage clearly indicates that the success of the American Revolution influenced other nations to pursue their quests for liberty, highlighting its impact on global movements for independence.</p>"}	8
RC		895	2	1	Challenges to the Necessity of Scientific Inquiry	Which of the following statements, if true, would most seriously weaken the argument that scientific inquiry is essential for societal advancement?	1	0	0	{}	2025-02-09 03:43:40.77	2025-02-09 03:43:40.77	t	98	50	t	{"solution": "<p>Option A is correct because it suggests that traditional practices can achieve effective results without reliance on scientific validation, thereby questioning the argument that scientific inquiry is essential for societal advancement.</p><p>Option B, while highlighting ethical dilemmas, does not directly weaken the argument but rather provides a criticism of scientific advancements. Hence, it does not challenge the necessity of scientific inquiry itself.</p><p>Option C indicates a public distrust in science, which could be seen as a criticism but does not weaken the argument regarding the overall importance of scientific inquiry in society.</p><p>Option D implies that effective solutions can arise from various fields, but it does not negate the value of scientific methods; therefore, it does not weaken the argument as strongly as Option A does.</p>"}	9
RC		896	2	1	The Implications of Peer Review in Science	What can be inferred about the role of peer review in the scientific process from the passage?	3	0	0	{}	2025-02-09 03:43:40.779	2025-02-09 03:43:40.779	t	98	50	t	{"solution": "<p>Option A is correct because the passage emphasizes that peer review is a mechanism that ensures research meets rigorous standards, thereby enhancing its credibility and quality.</p><p>Option B, although it may be true that peer review can cause delays, does not address the critical function of peer review in ensuring quality, making it less relevant to the inference.</p><p>Option C incorrectly suggests that peer review is unnecessary for already validated research. The process applies to all research submissions, regardless of prior validation, thus weakening the inference.</p><p>Option D implies that peer review is the sole method by which findings are verified, which is inaccurate as researchers utilize multiple methods for validation before public dissemination.</p>"}	9
RC		897	2	1	Fundamental Assumptions About Science Education	Which assumption underlies the argument that scientific education is crucial for fostering a scientifically literate society?	1	0	0	{}	2025-02-09 03:43:40.789	2025-02-09 03:43:40.789	t	98	50	t	{"solution": "<p>Option A is correct because it directly supports the argument that science education is essential for creating a scientifically literate society by implying a positive correlation between science education and future engagement with scientific topics.</p><p>Option B suggests that the educational system promotes critical thinking in all subjects, which, while potentially true, does not specifically support the argument about science education's unique role in fostering scientific literacy.</p><p>Option C incorrectly assumes that outside factors, such as personal experience or external influences, do not affect scientific literacy. This diminishes the relevance of the assumption about education alone.</p><p>Option D makes a broad claim about the universality of science, which does not directly relate to the argument regarding the necessity of science education for scientific literacy; therefore, it is not a valid assumption in this context.</p>"}	9
RC		898	2	1	The Significance of Science in Modern Society	What is the main idea of the passage regarding the significance of science in society?	4	0	0	{}	2025-02-09 03:43:40.798	2025-02-09 03:43:40.798	t	98	50	t	{"solution": "<p>Option A is correct because it encapsulates the central theme of the passage, emphasizing that science plays a crucial role in driving societal progress and tackling complex global issues.</p><p>Option B presents a critique of the scientific method in traditional practices but does not represent the main idea of the passage, which focuses on the positive contributions of science.</p><p>Option C highlights ethical dilemmas faced by scientific advancements, which is a significant concern but does not reflect the primary focus of the passage regarding science's importance to society.</p><p>Option D discusses the accessibility of education but is not aligned with the main idea, which centers around the value of scientific inquiry and its impact on societal development.</p>"}	9
\.


--
-- Data for Name: problemssettags; Type: TABLE DATA; Schema: public; Owner: compexe_admin
--

COPY public.problemssettags ("problemsSetId", tagid) FROM stdin;
\.


--
-- Data for Name: problemtags; Type: TABLE DATA; Schema: public; Owner: compexe_admin
--

COPY public.problemtags (problemid, tagid) FROM stdin;
541	132
541	133
541	134
541	135
542	132
542	136
542	137
542	138
543	139
543	140
543	141
543	142
544	139
544	136
544	143
544	142
545	132
545	140
545	144
545	138
546	139
546	133
546	134
546	145
547	132
547	136
547	143
547	146
548	132
548	136
548	147
548	148
549	139
549	133
549	149
549	148
550	132
550	140
550	150
550	151
551	139
551	133
551	149
551	148
552	132
552	136
552	137
552	148
553	139
553	136
553	147
553	138
554	132
554	136
554	147
554	135
555	139
555	133
555	149
555	146
556	132
556	140
556	152
556	153
557	139
557	136
557	143
557	145
558	139
558	133
558	134
558	146
559	132
559	140
559	150
559	154
560	139
560	140
560	152
560	151
561	139
561	133
561	134
561	135
562	132
562	133
562	134
562	146
563	132
563	140
563	141
563	138
573	155
574	155
575	156
576	157
577	155
578	156
579	158
580	159
581	155
582	156
583	158
584	156
585	155
586	156
587	160
587	161
588	162
588	163
588	164
588	165
589	160
589	166
590	160
590	167
591	160
591	166
592	168
593	168
594	162
594	169
594	164
594	170
595	160
595	171
596	160
596	167
597	160
597	172
598	162
598	173
598	164
598	174
607	169
607	175
607	176
607	177
608	178
608	175
608	176
608	177
677	179
677	180
678	179
678	181
679	179
679	181
689	179
689	181
691	179
691	182
692	179
692	182
693	179
693	183
704	184
704	185
705	186
705	187
706	188
706	189
707	190
707	189
708	191
708	192
709	193
710	194
711	195
712	195
713	196
714	197
715	196
716	190
716	187
717	188
717	192
718	184
718	185
719	191
719	189
720	198
720	185
721	199
721	185
722	194
723	194
724	200
725	194
726	195
727	196
728	196
729	197
730	196
815	132
815	136
815	201
815	138
816	139
816	133
816	149
816	145
817	139
817	140
817	141
817	142
818	139
818	136
818	208
818	202
819	132
819	140
819	152
819	153
820	132
820	140
820	141
820	138
821	139
821	133
821	134
821	145
822	139
822	133
822	134
822	146
609	132
609	133
609	134
609	135
610	132
610	136
610	137
610	138
611	139
611	140
611	141
611	142
612	139
612	136
612	143
612	142
613	132
613	140
613	144
613	138
614	139
614	133
614	134
614	145
615	132
615	136
615	143
615	146
616	132
616	136
616	147
616	148
617	139
617	133
617	149
617	148
618	132
618	140
618	150
618	151
619	139
619	133
619	149
619	148
620	132
620	136
620	137
620	148
621	139
621	136
621	147
621	138
622	132
622	136
622	147
622	135
623	139
623	133
623	149
623	146
624	132
624	140
624	152
624	153
625	139
625	136
625	143
625	145
626	139
626	133
626	134
626	146
627	132
627	140
627	150
627	154
628	139
628	140
628	152
628	151
629	139
629	133
629	134
629	135
630	132
630	133
630	134
630	146
631	132
631	140
631	141
631	138
641	155
642	155
643	156
644	157
645	155
646	156
647	158
648	159
649	155
650	156
651	158
652	156
653	155
654	156
655	160
655	161
656	162
656	163
656	164
656	165
657	160
657	166
658	160
658	167
659	160
659	166
660	168
661	168
662	162
662	169
662	164
662	170
663	160
663	171
664	160
664	167
665	160
665	172
666	162
666	173
666	164
666	174
675	169
675	175
675	176
675	177
676	178
676	175
676	176
676	177
731	132
731	136
731	201
731	153
732	139
732	140
732	141
732	202
733	139
733	136
733	137
733	202
734	132
734	133
734	134
734	146
735	132
735	140
735	150
735	151
736	139
736	140
736	141
736	203
737	139
737	133
737	134
737	146
738	132
738	136
739	132
739	133
739	149
739	145
740	139
740	140
740	150
740	154
741	139
741	136
741	143
741	153
742	132
742	133
742	149
742	148
743	139
743	140
743	144
743	203
744	132
744	136
744	137
744	151
745	139
745	136
745	143
745	135
746	139
746	136
747	132
747	133
747	134
747	148
748	139
748	133
748	134
748	148
749	132
749	140
749	144
749	202
750	132
750	140
750	141
750	153
751	132
751	133
751	149
751	148
823	139
823	136
823	137
823	203
761	179
761	183
762	179
762	204
763	179
763	180
765	179
765	180
774	179
774	204
776	179
776	205
777	179
777	205
778	179
778	206
779	179
779	204
788	186
788	187
789	198
789	192
790	190
790	192
791	199
791	185
792	184
792	189
793	191
793	192
794	197
795	196
796	197
797	207
798	196
799	197
800	199
800	185
801	184
801	185
802	198
802	189
803	184
803	192
804	186
804	189
805	188
805	187
806	193
807	196
808	200
809	196
810	197
811	194
812	196
813	197
814	196
824	132
824	136
824	201
824	142
825	132
825	140
825	152
825	202
826	139
826	133
826	134
826	148
827	139
827	136
827	137
827	151
828	132
828	140
828	144
828	203
829	139
829	136
829	137
829	202
830	132
830	140
473	132
473	133
473	134
473	135
474	132
474	136
474	137
474	138
475	139
475	140
475	141
475	142
476	139
476	136
476	143
476	142
477	132
477	140
477	144
477	138
478	139
478	133
478	134
478	145
479	132
479	136
479	143
479	146
480	132
480	136
480	147
480	148
481	139
481	133
481	149
481	148
482	132
482	140
482	150
482	151
483	139
483	133
483	149
483	148
484	132
484	136
484	137
484	148
485	139
485	136
485	147
485	138
486	132
486	136
486	147
486	135
487	139
487	133
487	149
487	146
488	132
488	140
488	152
488	153
489	139
489	136
489	143
489	145
490	139
490	133
490	134
490	146
491	132
491	140
491	150
491	154
492	139
492	140
492	152
492	151
493	139
493	133
493	134
493	135
494	132
494	133
494	134
494	146
495	132
495	140
495	141
495	138
505	155
506	155
507	156
508	157
509	155
510	156
511	158
512	159
513	155
514	156
515	158
516	156
517	155
518	156
519	160
519	161
520	162
520	163
520	164
520	165
521	160
521	166
522	160
522	167
523	160
523	166
524	168
525	168
526	162
526	169
526	164
526	170
527	160
527	171
528	160
528	167
529	160
529	172
530	162
530	173
530	164
530	174
539	169
539	175
539	176
539	177
540	178
540	175
540	176
540	177
830	150
830	142
831	139
831	133
831	149
831	148
832	132
832	140
832	144
832	151
833	132
833	136
833	208
833	142
834	132
834	133
834	149
834	148
835	132
835	133
835	149
835	148
845	179
845	181
846	179
846	183
847	179
847	205
849	179
849	180
857	179
857	181
859	179
859	206
860	179
860	183
861	179
861	183
871	179
871	204
872	186
872	185
873	188
873	187
874	186
874	192
875	184
875	192
876	198
876	189
877	195
878	195
879	197
880	196
881	195
882	197
883	196
884	186
884	185
885	190
885	187
886	198
886	185
887	198
887	189
888	188
888	192
889	190
889	189
890	207
891	195
892	197
893	195
894	197
895	193
896	195
897	197
898	196
\.


--
-- Data for Name: sections; Type: TABLE DATA; Schema: public; Owner: compexe_admin
--

COPY public.sections (sectionid, examtypeid, name, description) FROM stdin;
1	1	Quants	GRE Quantitative Questions
2	1	Verbal	GRE Verbal Ability Questions
3	2	Quants	GMAT Qunatitative Questions
4	2	Verbal	GMAT Verbal Ability Questions
5	2	Integrated Reasoning	GMAT Integrated Reasoning Questions
\.


--
-- Data for Name: tags; Type: TABLE DATA; Schema: public; Owner: compexe_admin
--

COPY public.tags (tagid, name, examtypeid, sectionid) FROM stdin;
132	Real Contextual	2	3
133	Algebra	2	3
134	Backsolving	2	3
135	Algebraic Equations	2	3
136	Word Problems	2	3
137	Assessing given Situation	2	3
138	Percentages	2	3
139	Pure Contextual	2	3
140	Arithmetic	2	3
141	Number Sense	2	3
142	Work and Time	2	3
143	Setting up proper steps	2	3
144	common pitfalls	2	3
145	Functions	2	3
146	Inequalities	2	3
147	Mathematical tools	2	3
148	Polynomials	2	3
149	Number Picking	2	3
150	Critical Reasoning	2	3
151	Unitary Method	2	3
152	Logical Reasoning	2	3
153	Trial and Error Method	2	3
154	Ratio and Proportion	2	3
155	Inference	2	4
156	Detail	2	4
157	Analyze the argument	2	4
158	Primary Purpose	2	4
159	Organization and Function	2	4
160	GI	2	5
161	Critical Thinking	2	5
162	TA	2	5
163	Comparative Analysis	2	5
164	Simple Table	2	5
165	Resource Management	2	5
166	Synthesis of Information	2	5
167	Quantitative Reasoning	2	5
168	Logistics and Supply Chain	2	5
169	Critical Reasoning	2	5
170	Business	2	5
171	Pattern Recognition	2	5
172	Attention to Detail	2	5
173	Data Synthesis	2	5
174	Marketing and Sales	2	5
175	Dicotomous Choice	2	5
176	MSR	2	5
177	Line Chart	2	5
178	Synthesis	2	5
179	DS	1	1
180	number theorm	1	1
181	linear inequalities	1	1
182	simple interest/compound interest	1	1
183	permutations and combinations	1	1
184	politics	1	2
185	tc-1	1	2
186	psychology	1	2
187	tc-2	1	2
188	philosophy	1	2
189	tc-3	1	2
190	economics	1	2
191	science	1	2
192	se	1	2
193	Weaken Question	1	2
194	Conclusion Question	1	2
195	Inference Question	1	2
196	Main Idea Question	1	2
197	Assumption Question	1	2
198	literature	1	2
199	history	1	2
200	Evaluate Question	1	2
201	Obtaining the best answer	2	3
202	Rates	2	3
203	Discount, Profit and Loss	2	3
204	geometry	1	1
205	Unitary method	1	1
206	profit, loss and discount	1	1
207	Strengthen Question	1	2
208	Choosing mathematical tools	2	3
\.


--
-- Data for Name: userattempt_selectedoptions; Type: TABLE DATA; Schema: public; Owner: compexe_admin
--

COPY public.userattempt_selectedoptions (id, userattemptid, optionid) FROM stdin;
\.


--
-- Data for Name: userattempts; Type: TABLE DATA; Schema: public; Owner: compexe_admin
--

COPY public.userattempts (attemptid, userid, problemid, timetaken, attemptdate, partialcorrectnessscore, iscorrect) FROM stdin;
1	1	829	0	2025-02-09 04:59:59.655	0.00	\N
2	1	830	0	2025-02-09 05:12:58.768	0.00	\N
3	1	677	0	2025-02-10 14:32:54.734	0.00	\N
4	1	541	0	2025-02-10 14:37:49.792	0.00	\N
5	1	566	0	2025-02-10 14:57:18.118	0.00	\N
6	1	678	0	2025-02-11 01:26:06.188	0.00	\N
7	1	681	0	2025-02-11 01:29:33.709	0.00	\N
8	1	679	0	2025-02-11 01:38:00.393	0.00	\N
9	1	682	0	2025-02-11 01:58:45.764	0.00	\N
10	1	719	0	2025-02-12 14:47:00.345	0.00	\N
11	1	558	0	2025-02-12 15:51:50.563	0.00	\N
12	1	820	0	2025-02-12 15:59:48.121	0.00	\N
13	1	476	0	2025-02-12 16:03:40.629	0.00	\N
14	1	886	0	2025-02-15 13:22:39.61	0.00	\N
15	1	804	0	2025-02-16 00:49:37.128	0.00	\N
16	1	788	0	2025-02-16 05:19:40.18	0.00	\N
17	1	762	0	2025-02-16 06:26:15.647	0.00	\N
18	1	805	0	2025-02-16 09:09:46.124	0.00	\N
19	1	885	0	2025-02-16 09:29:34.749	0.00	\N
20	1	716	0	2025-02-16 09:35:46.995	0.00	\N
21	1	705	0	2025-02-16 10:18:15.285	0.00	\N
22	1	876	0	2025-02-16 11:13:05.448	0.00	\N
23	1	709	0	2025-02-16 11:32:35.265	0.00	\N
24	1	706	0	2025-02-16 11:46:44.936	0.00	\N
25	1	887	0	2025-02-16 11:53:09.622	0.00	\N
26	1	789	0	2025-02-17 14:24:47.717	0.00	\N
27	1	680	0	2025-02-17 14:39:45.854	0.00	\N
28	1	708	0	2025-02-18 10:52:01.309	0.00	\N
29	1	717	0	2025-02-18 14:09:52.818	0.00	\N
30	1	690	0	2025-02-21 03:44:52.006	0.00	\N
31	1	695	0	2025-02-21 03:46:35.634	0.00	\N
32	1	775	0	2025-02-21 03:47:30.889	0.00	\N
33	1	698	0	2025-02-21 06:00:38.987	0.00	\N
34	1	697	0	2025-02-21 06:01:43.076	0.00	\N
35	1	858	0	2025-02-21 09:07:34.063	0.00	\N
36	1	863	0	2025-02-22 04:13:35.532	0.00	\N
37	1	696	0	2025-02-22 15:51:52.111	0.00	\N
38	1	764	0	2025-02-22 18:13:25.101	0.00	\N
39	1	872	0	2025-02-22 21:19:37.735	0.00	\N
40	1	596	0	2025-02-22 22:01:23.005	0.00	\N
41	1	792	0	2025-02-23 08:02:58.999	0.00	\N
42	1	595	0	2025-02-25 10:11:07.477	0.00	\N
43	1	527	0	2025-02-25 11:35:40.019	0.00	\N
44	1	542	0	2025-02-25 11:51:19.053	0.00	\N
45	1	543	0	2025-02-25 12:14:17.45	0.00	\N
46	1	790	0	2025-02-26 03:19:17.565	0.00	\N
\.


--
-- Data for Name: usermocktestattempts; Type: TABLE DATA; Schema: public; Owner: compexe_admin
--

COPY public.usermocktestattempts (attemptid, userid, mocktestid, starttime, endtime, totalscore, isofficialattempt) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: compexe_admin
--

COPY public.users (userid, username, password, email, registrationdate) FROM stdin;
1	admin	admin	admin@compex.com	2025-02-07 07:26:54.659
\.


--
-- Data for Name: userstreaks; Type: TABLE DATA; Schema: public; Owner: compexe_admin
--

COPY public.userstreaks (streakid, userid, currentstreak, lasttestdate, higheststreak) FROM stdin;
\.


--
-- Name: ProblemsSet_problemsSetId_seq; Type: SEQUENCE SET; Schema: public; Owner: compexe_admin
--

SELECT pg_catalog.setval('public."ProblemsSet_problemsSetId_seq"', 98, true);


--
-- Name: examtypes_examtypeid_seq; Type: SEQUENCE SET; Schema: public; Owner: compexe_admin
--

SELECT pg_catalog.setval('public.examtypes_examtypeid_seq', 1, false);


--
-- Name: mocksections_mocksectionid_seq; Type: SEQUENCE SET; Schema: public; Owner: compexe_admin
--

SELECT pg_catalog.setval('public.mocksections_mocksectionid_seq', 50, true);


--
-- Name: mocktestrankings_rankingid_seq; Type: SEQUENCE SET; Schema: public; Owner: compexe_admin
--

SELECT pg_catalog.setval('public.mocktestrankings_rankingid_seq', 1, false);


--
-- Name: mocktests_mocktestid_seq; Type: SEQUENCE SET; Schema: public; Owner: compexe_admin
--

SELECT pg_catalog.setval('public.mocktests_mocktestid_seq', 25, true);


--
-- Name: mocktestsectionscores_scoreid_seq; Type: SEQUENCE SET; Schema: public; Owner: compexe_admin
--

SELECT pg_catalog.setval('public.mocktestsectionscores_scoreid_seq', 1, false);


--
-- Name: problemoptions_optionid_seq; Type: SEQUENCE SET; Schema: public; Owner: compexe_admin
--

SELECT pg_catalog.setval('public.problemoptions_optionid_seq', 3922, true);


--
-- Name: problems_problemid_seq; Type: SEQUENCE SET; Schema: public; Owner: compexe_admin
--

SELECT pg_catalog.setval('public.problems_problemid_seq', 898, true);


--
-- Name: sections_sectionid_seq; Type: SEQUENCE SET; Schema: public; Owner: compexe_admin
--

SELECT pg_catalog.setval('public.sections_sectionid_seq', 1, false);


--
-- Name: tags_tagid_seq; Type: SEQUENCE SET; Schema: public; Owner: compexe_admin
--

SELECT pg_catalog.setval('public.tags_tagid_seq', 208, true);


--
-- Name: userattempt_selectedoptions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: compexe_admin
--

SELECT pg_catalog.setval('public.userattempt_selectedoptions_id_seq', 1, false);


--
-- Name: userattempts_attemptid_seq; Type: SEQUENCE SET; Schema: public; Owner: compexe_admin
--

SELECT pg_catalog.setval('public.userattempts_attemptid_seq', 46, true);


--
-- Name: usermocktestattempts_attemptid_seq; Type: SEQUENCE SET; Schema: public; Owner: compexe_admin
--

SELECT pg_catalog.setval('public.usermocktestattempts_attemptid_seq', 1, false);


--
-- Name: users_userid_seq; Type: SEQUENCE SET; Schema: public; Owner: compexe_admin
--

SELECT pg_catalog.setval('public.users_userid_seq', 1, false);


--
-- Name: userstreaks_streakid_seq; Type: SEQUENCE SET; Schema: public; Owner: compexe_admin
--

SELECT pg_catalog.setval('public.userstreaks_streakid_seq', 1, false);


--
-- Name: ProblemsSet ProblemsSet_pkey; Type: CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public."ProblemsSet"
    ADD CONSTRAINT "ProblemsSet_pkey" PRIMARY KEY ("problemsSetId");


--
-- Name: _prisma_migrations _prisma_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public._prisma_migrations
    ADD CONSTRAINT _prisma_migrations_pkey PRIMARY KEY (id);


--
-- Name: examtypes examtypes_pkey; Type: CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.examtypes
    ADD CONSTRAINT examtypes_pkey PRIMARY KEY (examtypeid);


--
-- Name: mocksections mocksections_pkey; Type: CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.mocksections
    ADD CONSTRAINT mocksections_pkey PRIMARY KEY (mocksectionid);


--
-- Name: mocktestrankings mocktestrankings_pkey; Type: CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.mocktestrankings
    ADD CONSTRAINT mocktestrankings_pkey PRIMARY KEY (rankingid);


--
-- Name: mocktests mocktests_pkey; Type: CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.mocktests
    ADD CONSTRAINT mocktests_pkey PRIMARY KEY (mocktestid);


--
-- Name: mocktestsectionscores mocktestsectionscores_pkey; Type: CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.mocktestsectionscores
    ADD CONSTRAINT mocktestsectionscores_pkey PRIMARY KEY (scoreid);


--
-- Name: performance performance_pkey; Type: CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.performance
    ADD CONSTRAINT performance_pkey PRIMARY KEY (userid, sectionid);


--
-- Name: problemoptions problemoptions_pkey; Type: CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.problemoptions
    ADD CONSTRAINT problemoptions_pkey PRIMARY KEY (optionid);


--
-- Name: problems problems_pkey; Type: CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.problems
    ADD CONSTRAINT problems_pkey PRIMARY KEY (problemid);


--
-- Name: problemssettags problemssettags_pkey; Type: CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.problemssettags
    ADD CONSTRAINT problemssettags_pkey PRIMARY KEY (tagid, "problemsSetId");


--
-- Name: problemtags problemtags_pkey; Type: CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.problemtags
    ADD CONSTRAINT problemtags_pkey PRIMARY KEY (problemid, tagid);


--
-- Name: sections sections_pkey; Type: CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.sections
    ADD CONSTRAINT sections_pkey PRIMARY KEY (sectionid);


--
-- Name: tags tags_pkey; Type: CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_pkey PRIMARY KEY (tagid);


--
-- Name: userattempt_selectedoptions userattempt_selectedoptions_pkey; Type: CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.userattempt_selectedoptions
    ADD CONSTRAINT userattempt_selectedoptions_pkey PRIMARY KEY (id);


--
-- Name: userattempts userattempts_pkey; Type: CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.userattempts
    ADD CONSTRAINT userattempts_pkey PRIMARY KEY (attemptid);


--
-- Name: usermocktestattempts usermocktestattempts_pkey; Type: CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.usermocktestattempts
    ADD CONSTRAINT usermocktestattempts_pkey PRIMARY KEY (attemptid);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (userid);


--
-- Name: userstreaks userstreaks_pkey; Type: CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.userstreaks
    ADD CONSTRAINT userstreaks_pkey PRIMARY KEY (streakid);


--
-- Name: userattempt_selectedoptions_userattemptid_optionid_key; Type: INDEX; Schema: public; Owner: compexe_admin
--

CREATE UNIQUE INDEX userattempt_selectedoptions_userattemptid_optionid_key ON public.userattempt_selectedoptions USING btree (userattemptid, optionid);


--
-- Name: users_email_key; Type: INDEX; Schema: public; Owner: compexe_admin
--

CREATE UNIQUE INDEX users_email_key ON public.users USING btree (email);


--
-- Name: users_username_key; Type: INDEX; Schema: public; Owner: compexe_admin
--

CREATE UNIQUE INDEX users_username_key ON public.users USING btree (username);


--
-- Name: ProblemsSet ProblemsSet_examtypeid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public."ProblemsSet"
    ADD CONSTRAINT "ProblemsSet_examtypeid_fkey" FOREIGN KEY (examtypeid) REFERENCES public.examtypes(examtypeid) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: ProblemsSet ProblemsSet_mocksectionid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public."ProblemsSet"
    ADD CONSTRAINT "ProblemsSet_mocksectionid_fkey" FOREIGN KEY (mocksectionid) REFERENCES public.mocksections(mocksectionid) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: ProblemsSet ProblemsSet_sectionid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public."ProblemsSet"
    ADD CONSTRAINT "ProblemsSet_sectionid_fkey" FOREIGN KEY (sectionid) REFERENCES public.sections(sectionid) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: mocksections mocksections_mocktestid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.mocksections
    ADD CONSTRAINT mocksections_mocktestid_fkey FOREIGN KEY (mocktestid) REFERENCES public.mocktests(mocktestid);


--
-- Name: mocksections mocksections_sectionid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.mocksections
    ADD CONSTRAINT mocksections_sectionid_fkey FOREIGN KEY (sectionid) REFERENCES public.sections(sectionid);


--
-- Name: mocktestrankings mocktestrankings_mocktestid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.mocktestrankings
    ADD CONSTRAINT mocktestrankings_mocktestid_fkey FOREIGN KEY (mocktestid) REFERENCES public.mocktests(mocktestid);


--
-- Name: mocktestrankings mocktestrankings_userid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.mocktestrankings
    ADD CONSTRAINT mocktestrankings_userid_fkey FOREIGN KEY (userid) REFERENCES public.users(userid);


--
-- Name: mocktests mocktests_examtypeid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.mocktests
    ADD CONSTRAINT mocktests_examtypeid_fkey FOREIGN KEY (examtypeid) REFERENCES public.examtypes(examtypeid);


--
-- Name: mocktestsectionscores mocktestsectionscores_attemptid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.mocktestsectionscores
    ADD CONSTRAINT mocktestsectionscores_attemptid_fkey FOREIGN KEY (attemptid) REFERENCES public.usermocktestattempts(attemptid);


--
-- Name: mocktestsectionscores mocktestsectionscores_sectionid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.mocktestsectionscores
    ADD CONSTRAINT mocktestsectionscores_sectionid_fkey FOREIGN KEY (sectionid) REFERENCES public.sections(sectionid);


--
-- Name: performance performance_sectionid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.performance
    ADD CONSTRAINT performance_sectionid_fkey FOREIGN KEY (sectionid) REFERENCES public.sections(sectionid);


--
-- Name: performance performance_userid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.performance
    ADD CONSTRAINT performance_userid_fkey FOREIGN KEY (userid) REFERENCES public.users(userid);


--
-- Name: problemoptions problemoptions_problemid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.problemoptions
    ADD CONSTRAINT problemoptions_problemid_fkey FOREIGN KEY (problemid) REFERENCES public.problems(problemid);


--
-- Name: problems problems_examtypeid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.problems
    ADD CONSTRAINT problems_examtypeid_fkey FOREIGN KEY (examtypeid) REFERENCES public.examtypes(examtypeid);


--
-- Name: problems problems_mocksectionid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.problems
    ADD CONSTRAINT problems_mocksectionid_fkey FOREIGN KEY (mocksectionid) REFERENCES public.mocksections(mocksectionid);


--
-- Name: problems problems_problemsSetId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.problems
    ADD CONSTRAINT "problems_problemsSetId_fkey" FOREIGN KEY ("problemsSetId") REFERENCES public."ProblemsSet"("problemsSetId");


--
-- Name: problems problems_sectionid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.problems
    ADD CONSTRAINT problems_sectionid_fkey FOREIGN KEY (sectionid) REFERENCES public.sections(sectionid);


--
-- Name: problemssettags problemssettags_problemsSetId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.problemssettags
    ADD CONSTRAINT "problemssettags_problemsSetId_fkey" FOREIGN KEY ("problemsSetId") REFERENCES public."ProblemsSet"("problemsSetId") ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: problemssettags problemssettags_tagid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.problemssettags
    ADD CONSTRAINT problemssettags_tagid_fkey FOREIGN KEY (tagid) REFERENCES public.tags(tagid) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: problemtags problemtags_problemid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.problemtags
    ADD CONSTRAINT problemtags_problemid_fkey FOREIGN KEY (problemid) REFERENCES public.problems(problemid);


--
-- Name: problemtags problemtags_tagid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.problemtags
    ADD CONSTRAINT problemtags_tagid_fkey FOREIGN KEY (tagid) REFERENCES public.tags(tagid);


--
-- Name: sections sections_examtypeid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.sections
    ADD CONSTRAINT sections_examtypeid_fkey FOREIGN KEY (examtypeid) REFERENCES public.examtypes(examtypeid);


--
-- Name: tags tags_examtypeid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_examtypeid_fkey FOREIGN KEY (examtypeid) REFERENCES public.examtypes(examtypeid);


--
-- Name: tags tags_sectionid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_sectionid_fkey FOREIGN KEY (sectionid) REFERENCES public.sections(sectionid);


--
-- Name: userattempt_selectedoptions userattempt_selectedoptions_optionid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.userattempt_selectedoptions
    ADD CONSTRAINT userattempt_selectedoptions_optionid_fkey FOREIGN KEY (optionid) REFERENCES public.problemoptions(optionid) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: userattempt_selectedoptions userattempt_selectedoptions_userattemptid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.userattempt_selectedoptions
    ADD CONSTRAINT userattempt_selectedoptions_userattemptid_fkey FOREIGN KEY (userattemptid) REFERENCES public.userattempts(attemptid) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: userattempts userattempts_problemid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.userattempts
    ADD CONSTRAINT userattempts_problemid_fkey FOREIGN KEY (problemid) REFERENCES public.problems(problemid);


--
-- Name: userattempts userattempts_userid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.userattempts
    ADD CONSTRAINT userattempts_userid_fkey FOREIGN KEY (userid) REFERENCES public.users(userid);


--
-- Name: usermocktestattempts usermocktestattempts_mocktestid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.usermocktestattempts
    ADD CONSTRAINT usermocktestattempts_mocktestid_fkey FOREIGN KEY (mocktestid) REFERENCES public.mocktests(mocktestid);


--
-- Name: usermocktestattempts usermocktestattempts_userid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.usermocktestattempts
    ADD CONSTRAINT usermocktestattempts_userid_fkey FOREIGN KEY (userid) REFERENCES public.users(userid);


--
-- Name: userstreaks userstreaks_userid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compexe_admin
--

ALTER TABLE ONLY public.userstreaks
    ADD CONSTRAINT userstreaks_userid_fkey FOREIGN KEY (userid) REFERENCES public.users(userid);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: compexe_admin
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;


--
-- PostgreSQL database dump complete
--

