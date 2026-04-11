export interface Analysis {
    id: string;
    name: string;
    date: string;
    type: string;
    grainSize: number;
    phases: { name: string; percentage: number }[];
    defects: number;
    status: "completed" | "processing" | "failed";
    image: string;
}

export const mockAnalyses: Analysis[] = [
    {
        id: "AN-1024",
        name: "ASTM E112 High Carbon Steel",
        date: "2024-04-10",
        type: "Martensitic Steel",
        grainSize: 12.4,
        phases: [
            { name: "Martensite", percentage: 85 },
            { name: "Retained Austenite", percentage: 15 },
        ],
        defects: 2,
        status: "completed",
        image: "/mock/steel-1.jpg",
    },
    {
        id: "AN-1025",
        name: "Gray Cast Iron Sample B",
        date: "2024-04-11",
        type: "Cast Iron",
        grainSize: 45.2,
        phases: [
            { name: "Ferrite", percentage: 40 },
            { name: "Pearlite", percentage: 60 },
        ],
        defects: 12,
        status: "completed",
        image: "/mock/iron-1.jpg",
    },
    {
        id: "AN-1026",
        name: "Tool Steel Heat Treatment #4",
        date: "2024-04-11",
        type: "Tool Steel",
        grainSize: 8.1,
        phases: [
            { name: "Carbides", percentage: 12 },
            { name: "Tempered Martensite", percentage: 88 },
        ],
        defects: 0,
        status: "completed",
        image: "/mock/steel-2.jpg",
    },
];

export const dashboardStats = [
    { label: "Total Analyses", value: "1,248", change: "+12%", trend: "up" },
    { label: "Avg Grain Size", value: "24.5 μm", change: "-2%", trend: "down" },
    { label: "Critical Defects", value: "3", change: "-40%", trend: "down" },
    { label: "AI Confidence", value: "99.2%", change: "+0.4%", trend: "up" },
];
