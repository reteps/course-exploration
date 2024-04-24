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

interface Course {
    number: string,
    department: string
}
interface CourseCredit extends Course {
    term: string,
    year: number,
    is_transfer: boolean,
    semester: number
}
interface Subrequirement {
    name: string,
    subreq_number: number,
    OK: boolean,
    needs: {
        hours: number,
        courses: number,
        course_list?: Course[]
    },
}
interface Requirement {
    name: string,
    req_number: number,
    OK: boolean,
    needs: {
        hours: number,
        courses: number,
        subreqs: number
    },
    subreqs: Subrequirement[]
}
export interface IAudit {
    requirements: Requirement[],
    student_id: string,
    courses_taken: CourseCredit[]
}
