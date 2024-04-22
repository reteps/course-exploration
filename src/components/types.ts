interface IDepartment {
    "% Sections using ICES"?: (number | null)[]
    "Top 10% Faculty"?: (number | null)[]
    "Next 20% Faculty"?: (number | null)[]
    "Middle 40% Faculty"?: (number | null)[]
    "Bottom 10% Faculty"?: (number | null)[]
    "Top 10% TA"?: (number | null)[]
    "Next 20% TA"?: (number | null)[]
    "Middle 40% TA"?: (number | null)[]
    "Bottom 10% TA"?: (number | null)[]
    "Faculty Count"?: number[]
    years: string[]
}

export interface IDataset {
    [key: string]: IDepartment
}

export type DepartmentKeys = Array<keyof IDepartment>;