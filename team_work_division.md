# Team Work Division (4 People)

Based on the technology stack, work is split into four roles that minimize overlap while keeping related technologies together.

---

## 1. Frontend Developer

**Focus:** Everything the user sees and interacts with.

| Layer | Technology |
|---|---|
| Frontend | Next.js + React + TypeScript |
| UI | Tailwind CSS + shadcn/ui |
| Maps (integration) | Open Street Map |

**Responsibilities:**
- Build all pages/screens using Next.js + React + TypeScript
- Implement UI components with Tailwind CSS + shadcn/ui, following the design system
- Integrate maps (location pickers, live tracking views)
- Consume APIs from the Backend Developer
- Handle client-side auth state (via Firebase Authentication SDK)
- Responsive design (mobile/tablet/desktop)

---

## 2. Backend Developer

**Focus:** APIs, business logic, and server-side integrations.

| Layer | Technology |
|---|---|
| Backend/API | FastAPI + Python |
| Serverless Logic | Firebase Cloud Functions |
| SMS | SMS gateway/API |
| Cache | Redis *(optional, post-MVP)* |

**Responsibilities:**
- Design and build REST/GraphQL endpoints with FastAPI
- Write Firebase Cloud Functions for event-driven logic (triggers on Firestore writes, etc.)
- Integrate SMS gateway for OTP/notifications
- Define API contracts for the Frontend team
- Set up Redis caching later if performance requires it

---

## 3. Database & Infrastructure Engineer

**Focus:** Data layer, storage, auth rules, and deployment pipeline.

| Layer | Technology |
|---|---|
| Database | Firebase Firestore |
| Authentication | Firebase Authentication |
| Real-time Queue | Firestore real-time listeners |
| File Storage | Firebase Storage |
| Notifications | Firebase Cloud Messaging (FCM) |
| Deployment | Vercel + Firebase |
| Version Control | GitHub |

**Responsibilities:**
- Design Firestore data models/schema and security rules
- Configure Firebase Authentication (roles, permissions)
- Implement real-time listeners for queue/status updates
- Set up Firebase Storage buckets and access rules
- Configure FCM for push notifications
- Manage CI/CD, deployments (Vercel + Firebase), and GitHub repo/branching strategy

---

## 4. AI/ML Engineer

**Focus:** Data science and intelligent features.

| Layer | Technology |
|---|---|
| AI/ML | Python + Scikit-learn |

**Responsibilities:**
- Build and train ML models (e.g., queue prediction, demand forecasting, recommendations)
- Expose model predictions via an API endpoint (works closely with Backend Developer to integrate into FastAPI)
- Prepare/clean data pulled from Firestore for training
- Monitor and retrain models as needed

---

## Collaboration Notes

- **Frontend ↔ Backend:** Agree on API contracts early (request/response shapes).
- **Backend ↔ Database/Infra:** Backend consumes Firestore via Admin SDK; Infra owns schema/security rules.
- **AI/ML ↔ Backend:** ML model outputs are served through a Backend-owned endpoint, not called directly by Frontend.
- **Database/Infra** owns the deployment pipeline, so all merges to `main` should go through them (or an agreed CI/CD process) for release.
