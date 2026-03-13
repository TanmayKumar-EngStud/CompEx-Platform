"use client";
import React, { useState } from "react";
import {
   startOfMonth,
   endOfMonth,
   startOfWeek,
   endOfWeek,
   addDays,
   format,
   addMonths,
   subMonths,
   isSameMonth,
   isSameDay,
} from "date-fns";

const Calendar: React.FC = () => {
   const [currentMonth, setCurrentMonth] = useState(new Date());

   const renderHeader = () => {
      const dateFormat = "MMMM yyyy";

      return (
         <div className="flex justify-between items-center mb-4">
            <div
               className="cursor-pointer p-2 rounded-full hover:bg-muted text-foreground"
               onClick={() => setCurrentMonth(subMonths(currentMonth, 1))}
            >
               <span>&lt;</span>
            </div>
            <div>
               <span className="text-lg font-medium text-foreground">
                  {format(currentMonth, dateFormat)}
               </span>
            </div>
            <div
               className="cursor-pointer p-2 rounded-full hover:bg-muted text-foreground"
               onClick={() => setCurrentMonth(addMonths(currentMonth, 1))}
            >
               <span>&gt;</span>
            </div>
         </div>
      );
   };

   const renderDays = () => {
      const days = [];
      const dateFormat = "eeeeee";
      const startDate = startOfWeek(currentMonth);

      for (let i = 0; i < 7; i++) {
         days.push(
            <div
               className="text-center w-10 h-10 font-bold flex justify-center items-center text-muted-foreground"
               key={i}
            >
               {format(addDays(startDate, i), dateFormat)}
            </div>
         );
      }

      return <div className="grid grid-cols-7">{days}</div>;
   };

   const renderCells = () => {
      const monthStart = startOfMonth(currentMonth);
      const monthEnd = endOfMonth(currentMonth);
      const startDate = startOfWeek(monthStart);
      const endDate = endOfWeek(monthEnd);

      const dateFormat = "d";
      const rows = [];
      let days = [];
      let day = startDate;
      let formattedDate = "";

      while (day <= endDate) {
         for (let i = 0; i < 7; i++) {
            formattedDate = format(day, dateFormat);
            const cloneDay = day;
            days.push(
               <div
                  className={`text-center cursor-pointer w-10 h-10 flex items-center justify-center transition-colors
                     ${
                        !isSameMonth(day, monthStart)
                           ? "text-muted-foreground/50"
                           : isSameDay(day, new Date())
                           ? "bg-primary text-primary-foreground rounded-full"
                           : "text-foreground hover:bg-muted/50 rounded-full"
                     }`}
                  key={day.toString()}
                  onClick={() => {
                     console.log(cloneDay);
                  }}
               >
                  <span>{formattedDate}</span>
               </div>
            );
            day = addDays(day, 1);
         }
         rows.push(
            <div className="grid grid-cols-7" key={day.toString()}>
               {days}
            </div>
         );
         days = [];
      }

      return <div>{rows}</div>;
   };

   return (
      <div className="max-w-md min-w-[28rem] mt-10 mx-auto p-4 bg-card text-card-foreground rounded-lg shadow-md border border-border">
         {renderHeader()}
         {renderDays()}
         {renderCells()}
      </div>
   );
};

export default Calendar;
