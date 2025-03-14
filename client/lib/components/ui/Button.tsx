/* eslint-disable */
import {Tooltip, TooltipContent, TooltipProvider, TooltipTrigger,} from "@radix-ui/react-tooltip";
import {cva, type VariantProps} from "class-variance-authority";
import {ButtonHTMLAttributes, forwardRef, Ref, RefAttributes} from "react";
import {FaSpinner} from "react-icons/fa";

import {cn} from "@/lib/utils";

const ButtonVariants = cva(
    "px-8 py-3 text-sm disabled:opacity-80 text-center font-medium rounded-md focus:ring ring-primary/10 outline-none flex items-center justify-center gap-2 transition-opacity focus:ring-0",
    {
        variants: {
            variant: {
                primary:
                    "bg-primary border border-black dark:border-white disabled:bg-gray-500 disabled:hover:bg-gray-500 text-white dark:bg-white dark:text-black hover:bg-gray-700 dark:hover:bg-gray-200 transition-colors",
                tertiary:
                    "text-black dark:text-white bg-transparent py-2 px-4 disabled:opacity-25",
                secondary:
                    "border border-black dark:border-white bg-white dark:bg-black text-black dark:text-white focus:bg-black dark:focus:bg-white hover:bg-black dark:hover:bg-white hover:text-white dark:hover:text-black focus:text-white dark:focus:text-black transition-colors shadow-none",
                danger:
                    "border border-red-500 hover:bg-red-500 hover:text-white transition-colors",
            },
            brightness: {
                dim: "",
                default: "",
            },
        },
        defaultVariants: {
            variant: "primary",
            brightness: "default",
        },
    }
);

export interface ButtonProps
    extends ButtonHTMLAttributes<HTMLButtonElement>,
        VariantProps<typeof ButtonVariants> {
    isLoading?: boolean;
    tooltip?: string;
}

const Button = forwardRef(
    (
        {
            className,
            children,
            variant,
            brightness,
            isLoading,
            tooltip,
            ...props
        }: ButtonProps,
        forwardedRef
    ): JSX.Element => {
        const buttonProps: ButtonProps & RefAttributes<HTMLButtonElement> = {
            className: cn(ButtonVariants({variant, brightness, className})),
            disabled: isLoading,
            ...props,
            ref: forwardedRef as Ref<HTMLButtonElement> | undefined,
        };

        const buttonChildren = (
            <>
                {children} {isLoading && <FaSpinner className="animate-spin"/>}
            </>
        );

        if (tooltip !== undefined) {
            return (
                <TooltipProvider>
                    <Tooltip>
                        <TooltipTrigger {...buttonProps}>{buttonChildren}</TooltipTrigger>
                        <TooltipContent className="bg-gray-100 rounded-md p-1">
                            {tooltip}
                        </TooltipContent>
                    </Tooltip>
                </TooltipProvider>
            );
        }

        return <button {...buttonProps}>{buttonChildren}</button>;
        // return <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
        //     {buttonChildren}
        // </button>;
    }
);

export default Button;
