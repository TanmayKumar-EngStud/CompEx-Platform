"use client";
import { useEffect, useMemo, useCallback } from "react";
import React from "react";
import { TagLinks } from "@/shared/components/ui/button";
import { usePaginationStore } from "@/shared/stores/problems/pagination";
import { Tag } from "@/features/question-solving/hooks/(definitions)/tagDefinition";
import { useState } from "react";
import { Switch } from "@/shared/components/ui/switch";

interface SectionPromps {
   tagData: Tag[];
   displaySolvedQuestions: boolean;
   setDisplaySolvedQuestions: React.Dispatch<React.SetStateAction<boolean>>;
}

const Section: React.FC<SectionPromps> = React.memo(function Section({
   tagData = [],
   displaySolvedQuestions,
   setDisplaySolvedQuestions,
}) {
   const {
      selectedTopics, setSelectedTopics,
      selectedThemes, setSelectedThemes,
      selectedTypes, setSelectedTypes
   } = usePaginationStore();

   const categories = useMemo(() => {
      console.log("DEBUG: Raw tagData received by Section:", tagData);
      if (!Array.isArray(tagData)) return { topics: [], themes: [], types: [] };

      const topicMap = new Map<string, number>();
      const themeMap = new Map<string, number>();
      const typeMap = new Map<string, number>();

      tagData.forEach(tag => {
         if (tag.topic && typeof tag.topic === 'string' && tag.topic.trim() !== "") {
            topicMap.set(tag.topic, (topicMap.get(tag.topic) || 0) + tag.count);
         }
         if (tag.theme && typeof tag.theme === 'string' && tag.theme.trim() !== "") {
            themeMap.set(tag.theme, (themeMap.get(tag.theme) || 0) + tag.count);
         }
         if (tag.type && typeof tag.type === 'string' && tag.type.trim() !== "") {
            typeMap.set(tag.type, (typeMap.get(tag.type) || 0) + tag.count);
         }
      });

      const result = {
         topics: Array.from(topicMap.entries())
            .map(([name, count]) => ({ name, count }))
            .filter(t => t.name && t.name.trim().length > 0),
         themes: Array.from(themeMap.entries())
            .map(([name, count]) => ({ name, count }))
            .filter(t => t.name && t.name.trim().length > 0),
         types: Array.from(typeMap.entries())
            .map(([name, count]) => ({ name, count }))
            .filter(t => t.name && t.name.trim().length > 0),
      };

      console.log("DEBUG: Category aggregation result:", result);
      return result;
   }, [tagData]);

   const toggleSelection = (category: 'topic' | 'theme' | 'type', name: string) => {
      if (category === 'topic') {
         setSelectedTopics(
            selectedTopics.includes(name)
               ? selectedTopics.filter(t => t !== name)
               : [...selectedTopics, name]
         );
      } else if (category === 'theme') {
         setSelectedThemes(
            selectedThemes.includes(name)
               ? selectedThemes.filter(t => t !== name)
               : [...selectedThemes, name]
         );
      } else if (category === 'type') {
         setSelectedTypes(
            selectedTypes.includes(name)
               ? selectedTypes.filter(t => t !== name)
               : [...selectedTypes, name]
         );
      }
   };

   const renderCategory = (title: string, items: { name: string, count: number }[], selectedItems: string[], category: 'topic' | 'theme' | 'type') => (
      <div className="mb-6">
         <h3 className="text-lg font-semibold mb-3 text-foreground/80">{title}</h3>
         <div className="flex flex-wrap gap-3">
            {items.map((item, idx) => (
               <div onClick={() => toggleSelection(category, item.name)} key={`${category}-${idx}`}>
                  <TagLinks
                     name={item.name}
                     count={item.count}
                     isActive={selectedItems.includes(item.name)}
                     href="#"
                     color1={null}
                     color2={null}
                  />
               </div>
            ))}
         </div>
      </div>
   );

   return (
      <div className="w-full flex flex-col justify-between">
         <div className="space-y-2">
            {categories.topics.length > 0 && renderCategory("Topics", categories.topics, selectedTopics, 'topic')}
            {categories.themes.length > 0 && renderCategory("Themes", categories.themes, selectedThemes, 'theme')}
            {categories.types.length > 0 && renderCategory("Types", categories.types, selectedTypes, 'type')}
         </div>

         <div className="flex justify-end mt-3 gap-4 items-center border-t pt-4">
            <span className="text-foreground">
               Display solved questions:
            </span>{" "}
            <Switch
               checked={displaySolvedQuestions}
               onCheckedChange={() => {
                  setDisplaySolvedQuestions(!displaySolvedQuestions);
               }}
            />
         </div>
      </div>
   );
});

export default Section;
