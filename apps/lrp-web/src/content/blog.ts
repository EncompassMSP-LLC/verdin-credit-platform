export type BlogPost = {
  slug: string;
  title: string;
  description: string;
  date: string;
  readingMinutes: number;
  category: string;
  author: string;
  content: string[];
};

export const blogPosts: BlogPost[] = [
  {
    slug: 'invisible-readiness-pipeline-fallout',
    title: 'Invisible readiness is where good loans stall',
    description:
      'Why near-miss borrowers fall out between pre-qualification and clear-to-close—and how shared readiness language changes the outcome.',
    date: '2026-06-12',
    readingMinutes: 7,
    category: 'Operations',
    author: 'LRP Insights',
    content: [
      'Every production leader knows the pattern: a borrower looks close enough to pursue, a realtor sets a timeline, and then the file stalls in a fog of credit updates, document requests, and status messages that mean different things to different people.',
      'The failure mode is rarely a single dramatic underwriting denial. More often it is incomplete readiness—fragmented across bureau findings, dispute cycles, income documentation, and partner handoffs. When readiness is invisible, optimism fills the gaps. When optimism meets conditions, fallout follows.',
      'Lending readiness is a system outcome. It requires a shared definition of blockers, ownership of next actions, and signals that underwriting can respect. Teams that treat readiness as a scoreboard slogan keep repeating the same cycle. Teams that treat it as an operating rhythm recover volume without compromising judgment.',
      'Start by naming the near-miss segment you already want to fund. Define stages in plain language. Require mediated controls for high-risk credit work. Export readiness summaries that explain what changed and what remains. The goal is not theater. The goal is fewer surprises between almost ready and lending ready.',
    ],
  },
  {
    slug: 'staff-mediated-controls-trust',
    title: 'Why staff-mediated controls are a growth feature',
    description:
      'Compliance-minded workflow design is not a brake on production. It is how serious lenders scale readiness partnerships.',
    date: '2026-05-28',
    readingMinutes: 6,
    category: 'Trust',
    author: 'LRP Insights',
    content: [
      'In consumer-credit adjacent software, “fully autonomous” is often sold as speed. For mortgage institutions, unsupervised high-risk actions are usually a liability—operationally, reputationally, and regulatorily.',
      'Staff-mediated controls put professional judgment where it belongs: on dispute-adjacent work, sensitive data access, and partner communications that can create unfair or misleading expectations. Audit trails turn tribal knowledge into inspectable process.',
      'Far from slowing production, mediation reduces rework. Files that advance with evidenced readiness create fewer late-stage surprises. Compliance stakeholders can evaluate a vendor on controls instead of slogans. Production teams can promise timelines they can defend.',
      'If a readiness partner cannot explain who acts, who reviews, and what is logged, they are asking your institution to outsource trust. Serious lenders should decline.',
    ],
  },
  {
    slug: 'realtor-expectation-setting',
    title: 'Expectation-setting scripts that protect closings',
    description:
      'Realtors do not need another credit pitch. They need honest readiness stages that keep client trust intact.',
    date: '2026-05-08',
    readingMinutes: 5,
    category: 'Partners',
    author: 'LRP Insights',
    content: [
      'Top-producing agents lose deals in two ways that credit complexity makes worse: clients feel abandoned during long remediation cycles, or they are coached into contract timelines the file cannot support.',
      'Preferred-partner programs work when readiness stages are plain and consistent. “Diagnose complete,” “remediation in progress,” and “partner review ready” beat vague updates like “we’re working on disputes.” Agents can set expectations without selling outcomes they cannot control.',
      'The brand standard is dignity. Borrowers should never be reduced to shame narratives. Lenders should never be asked to rubber-stamp unverified progress. Realtors should remain guides—not substitute credit operators.',
      'Equip your channel with a short stage glossary, a weekly update cadence, and a clear escalation path. Closings improve when language improves.',
    ],
  },
  {
    slug: 'readiness-is-not-a-single-score',
    title: 'Readiness is not a single score',
    description:
      'A bureau number is an input. Lending readiness is the coordinated state of credit integrity, documentation, and partner clarity.',
    date: '2026-04-22',
    readingMinutes: 6,
    category: 'Strategy',
    author: 'LRP Insights',
    content: [
      'Scores are familiar. Institutions already consume them. The mistake is treating a score movement as proof that a borrower is lending ready.',
      'A file can show an improved score and still fail on tradeline explanations, thin documentation, unresolved conditions, or partner miscommunication. Conversely, a borrower with a modest score can be operationally ready when findings are clear, evidence is packaged, and next actions are owned.',
      'That is why Lending Readiness Partners emphasizes diagnosis, orchestration, signaling, and advancement as a path. Metrics matter. Explainability matters more. Underwriting still decides.',
      'If your team’s dashboard celebrates points without showing blockers and evidence, you are measuring activity—not readiness.',
    ],
  },
];

export function getPost(slug: string): BlogPost | undefined {
  return blogPosts.find((post) => post.slug === slug);
}
