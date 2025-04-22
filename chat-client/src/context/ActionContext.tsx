import React, { createContext, useState, useContext, ReactNode } from 'react'
import { Action } from '../types'

interface ActionContextType {
	pdf_action: Action
    pdf_snippet: string | null
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
	const [pdf_action, setAction] = useState<Action>(Action.Default)
    const [pdf_snippet, setSnippet] = useState<string>('')


	return (
		<ActionContext.Provider
			value={{ pdf_action, pdf_snippet, setAction, setSnippet }}
		>
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