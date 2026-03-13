import React from "react";
import clsx from "clsx";
interface FooterProps {
   leftItems?: React.ReactNode[];
   centerItems?: React.ReactNode[];
   rightItems?: React.ReactNode[];
   gap?: number;
   className?: string;
}

const Footer: React.FC<FooterProps> = ({
   leftItems = [],
   centerItems = [],
   rightItems = [],
   gap = 5,
   className = "",
}) => {
   const flexgap = `gap-${gap}`;
   const itemclass = `flex justify-around items-center space-x-4 w-full`;
   return (
      <footer
         className={clsx(
            "flex flex-row justify-between items-center py-4 px-6 shadow-mt mt-4",
            className,
            flexgap
         )}
      >
         {Number(leftItems.length) ? (
            <div className={clsx(itemclass)}>
               {leftItems.map((item, index) => (
                  <React.Fragment key={index}>{item}</React.Fragment>
               ))}
            </div>
         ) : (
            <></>
         )}
         {Number(centerItems.length) ? (
            <div className={clsx(itemclass)}>
               {centerItems.map((item, index) => (
                  <React.Fragment key={index}>{item}</React.Fragment>
               ))}
            </div>
         ) : (
            <></>
         )}
         {Number(rightItems.length) ? (
            <div className={clsx(itemclass)}>
               {rightItems.map((item, index) => (
                  <React.Fragment key={index}>{item}</React.Fragment>
               ))}
            </div>
         ) : (
            <></>
         )}
      </footer>
   );
};
export default Footer;
