import { useRef, useState } from 'react'
import { patchMe, uploadAvatar } from '../../../../api/authWrapper'
import { User } from '../../../../types/User'

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
            const updated = await patchMe({ [editingField]: editValue })
            setUser({
                id:       updated.user.id       ?? user.id,
                username: updated.user.username ?? user.username,
                email:    updated.user.email    ?? user.email,
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
        try {
            const updated = await uploadAvatar(user.id, file)
            setUser({
                id:       updated.user.id       ?? user.id,
                username: updated.user.username ?? user.username,
                email:    updated.user.email    ?? user.email,
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
