import { Router, type IRouter } from "express";
import healthRouter from "./health";
import auraSphereRouter from "./aura-sphere";
import chatRouter from "./chat";
import stubV1Router from "./stub-v1";
import skillsRouter from "./skills";
import nexusAiRouter from "./nexus-ai";
import hubItemsRouter from "./creator-hub/items";
import hubThemesRouter from "./creator-hub/themes";
import hubAgentsRouter from "./creator-hub/agents";
import hubSkillsRouter from "./creator-hub/skills";
import hubProjectsRouter from "./creator-hub/projects";

const router: IRouter = Router();

router.use(healthRouter);
router.use(nexusAiRouter);
router.use(auraSphereRouter);
router.use(chatRouter);
router.use(stubV1Router);
router.use(skillsRouter);
router.use("/items", hubItemsRouter);
router.use("/themes", hubThemesRouter);
router.use("/agents", hubAgentsRouter);
router.use("/skills", hubSkillsRouter);
router.use("/projects", hubProjectsRouter);

export default router;
