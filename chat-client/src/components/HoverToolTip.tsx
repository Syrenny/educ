import React from 'react'

interface TooltipProps {
	label?: string
	position?: 'top' | 'bottom' | 'left' | 'right'
	TooltipClassNames?: string
	children: React.ReactNode
}

const positionClasses: Record<string, string> = {
	top: 'bottom-full mb-2',
	bottom: 'top-full mt-2',
	left: 'right-full mr-2 top-1/2 -translate-y-1/2',
	right: 'left-full ml-2 top-1/2 -translate-y-1/2',
}

const HoverTooltip: React.FC<TooltipProps> = ({
	label = '',
	position = 'bottom',
	TooltipClassNames = '',
	children,
}) => {
	return (
		<div className='group relative inline-block md:relative'>
			{children}

			<div
				className={`
					invisible absolute z-10 w-64 whitespace-normal rounded-md bg-black p-2 text-center text-white
					group-hover:visible group-active:visible
					max-sm:left-1/2 max-sm:-translate-x-1/2
					${positionClasses[position] || ''}
					${TooltipClassNames}
				`}
			>
				{label}
			</div>
		</div>
	)
}

export default HoverTooltip
