import React, { createContext, useState, useContext, ReactNode } from 'react'
import type { Shortcut } from '../types'

interface ShortcutContextType {
	shortcut: Shortcut | null
	setShortcut: (shortcut: Shortcut) => void
}

const ShortcutContext = createContext<ShortcutContextType | null>(
	null
)

interface ShortcutContextProviderProps {
	children: ReactNode
}

export const ShortcutContextProvider: React.FC<ShortcutContextProviderProps> = ({
	children,
}) => {
	const [shortcut, setShortcut] = useState<Shortcut | null>(null)

	return (
		<ShortcutContext.Provider value={{ shortcut, setShortcut }}>
			{children}
		</ShortcutContext.Provider>
	)
}

export const useShortcut = () => {
    const context = useContext(ShortcutContext)
    if (!context) {
        throw new Error('useShortcut must be used within an ShortcutProvider')
    }
    return context
}