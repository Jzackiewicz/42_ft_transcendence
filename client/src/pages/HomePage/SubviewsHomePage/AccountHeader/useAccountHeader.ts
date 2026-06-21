import { useRef, useState } from 'react'
import { patchMe, uploadAvatar } from '../../../../api/authWrapper'
import { User } from '../../../../types/User'

const AVATAR_MAX_SIZE_MB = 2

function convertMB(mb: number): number {
    return mb * 1024 * 1024
}

export function useAccountHeader(user: User | null | undefined, setUser: (u: User | null) => void) {
    const [editingField, setEditingField] = useState<'username' | 'email' | null>(null)
    const [editValue, setEditValue] = useState('')
    const [error, setError] = useState<string | null>(null)
    const fileInputRef = useRef<HTMLInputElement>(null)

    const startEdit = (field: 'username' | 'email') => {
        setEditingField(field)
        setEditValue(user?.[field] ?? '')
        setError(null)
    }

    const cancelEdit = () => {
        setEditingField(null)
        setEditValue('')
        setError(null)
    }

    const confirmEdit = async () => {
        if (!editingField || !user) return
        try {

            if (editingField === 'username') {
                if (editValue.trim().length < 3) {
                    setError('Username must be at least 3 characters.')
                    return
                }
                if (editValue.length > 40) {
                    setError('This Field must be 40 characters or fewer.')
                    return
                }
            }
            if (editingField === 'email') {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
                if (!emailRegex.test(editValue)) {
                    setError('Please enter a valid email address.')
                    return
                }
                if (editValue.trim().length > 254) {
                    setError('This Field must be 254 characters max')
                    return
                }

            }
            const updated = await patchMe({ [editingField]: editValue })
            setUser({
                id:       updated.user.id       ?? user.id,
                username: updated.user.username ?? user.username,
                email:    updated.user.email    ?? user.email,
                date_joined: updated.user.dateJoin ?? user.dateJoin,
                avatar:   updated.avatar        ?? user.avatar,
            })
            setEditingField(null)
        } catch (e: any) {
            const data = e?.response?.data
            const firstField = Object.values(data ?? {})[0]
            const message = data?.detail ?? (Array.isArray(firstField) ? firstField[0] : null) ?? 'Update failed.'
            setError(message)
        }
    }

    const handleAvatarClick = () => fileInputRef.current?.click()

    const handleAvatarChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (!file || !user) return
        if (file.size > convertMB(AVATAR_MAX_SIZE_MB)) {
            setError(`Avatar must be smaller than ${AVATAR_MAX_SIZE_MB}MB.`)
            return
        }
            
        try {
            const updated = await uploadAvatar(user.id, file)
            setUser({
                id:       updated.user.id       ?? user.id,
                username: updated.user.username ?? user.username,
                email:    updated.user.email    ?? user.email,
                date_joined: updated.user.dateJoin ?? user.dateJoin,
                avatar:   updated.avatar        ?? user.avatar,
            })
        } catch (e: any) {
            setError(e?.response?.data?.detail ?? 'Avatar upload failed.')
        }
        e.target.value = ''
    }

    return {
        editingField, editValue, setEditValue, error,
        startEdit, cancelEdit, confirmEdit,
        fileInputRef, handleAvatarClick, handleAvatarChange,
    }
}
