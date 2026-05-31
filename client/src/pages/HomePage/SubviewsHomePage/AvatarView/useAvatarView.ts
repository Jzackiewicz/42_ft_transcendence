import { useState } from 'react'

export interface AvatarPreset {
    grad:     string
    initials: string
}

// gradient is defind here as instead the gradient could be the img
export const AVATAR_PRESETS: AvatarPreset[] = [
    { grad: 'linear-gradient(135deg,#00e5ff,#0088aa)', initials: 'MK' },
    { grad: 'linear-gradient(135deg,#e040fb,#880088)', initials: 'VX' },
    { grad: 'linear-gradient(135deg,#ffc400,#e65100)', initials: 'JL' },
    { grad: 'linear-gradient(135deg,#00e676,#00695c)', initials: 'RO' },
    { grad: 'linear-gradient(135deg,#ff1744,#880e4f)', initials: 'AX' },
    { grad: 'linear-gradient(135deg,#7c4dff,#311b92)', initials: 'SY' },
]

export function useAvatarView(initialIndex = 0) {
    const [selectedIndex, setSelectedIndex] = useState(initialIndex)

    const selectedPreset = AVATAR_PRESETS[selectedIndex]

    return { selectedIndex, setSelectedIndex, selectedPreset }
}

