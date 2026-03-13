const ArrowIcons = ({ up, down }: { up?: boolean; down?: boolean }) => {
   return (
      <div>
         <div>
            {up ? (
               <i className="fas fa-caret-up text-sg m-0 p-0"></i>
            ) : (
               <div className="w-5"> </div>
            )}
            {down ? (
               <i className="fas fa-caret-down text-sg m-0 p-0"></i>
            ) : (
               <div className="w-5"> </div>
            )}
         </div>
      </div>
   );
};

export default ArrowIcons;
