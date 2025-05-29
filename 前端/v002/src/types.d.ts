// 合辑类型
interface Collection {
    id: number
    name: string
    description?: string
    creatorId: number
    createdAt: Date
    categories: Category[]
}

// 分类类型（兼容原ClassificationA组件）
interface Category {
    id: number
    collectionId: number
    name: string
    progress: number
    locked: boolean
    videos: Video[]
    homeworks: Homework[]
    materials: Material[]
}

// 视频类型（兼容原VideoList）
interface Video {
    id: number
    categoryId: number
    title: string
    description: string
    thumbnail: string
    url: string
    duration: string
}

// 作业类型（兼容原HomeworkList）
interface Homework {
    id: number
    categoryId: number
    title: string
    description: string
    deadline: string
    status: 'pending' | 'completed'
}

// 资料类型（兼容原MaterialList）
interface Material {
    id: number
    categoryId: number
    title: string
    type: 'doc' | 'video' | 'code'
    description: string
    url: string
    date: string
}

// 用户类型（新增认证模块）
interface User {
    id: number
    username: string
    role: 'admin' | 'user'
    unlockedCollections: number[]
}

// 导出类型
export type { Collection, Category, Video, Homework, Material, User }