import React, { createContext, useState, useContext, ReactNode } from 'react'
import { Action } from '../types'

interface ActionContextType {
	action: Action
    snippet: string | null
	setAction: (action: Action) => void
    setSnippet: (snippet: string) => void
}

const ActionContext = createContext<ActionContextType | null>(null)

interface ActionContextProviderProps {
	children: ReactNode
}

export const ActionContextProvider: React.FC<ActionContextProviderProps> = ({
	children,
}) => {
	const [action, setAction] = useState<Action>(Action.Default)
    const [snippet, setSnippet] = useState<string>("")


	return (
		<ActionContext.Provider value={{ action, snippet, setAction, setSnippet }}>
			{children}
		</ActionContext.Provider>
	)
}

export const useAction = () => {
    const context = useContext(ActionContext)
    if (!context) {
        throw new Error('useShortcut must be used within an ActionProvider')
    }
    return context
}