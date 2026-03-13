"use client";
import { useQuery } from "@tanstack/react-query";
import { useState, useEffect } from "react";

import { Tag } from "../(definitions)/tagDefinition";
import { usePaginationStore } from "@/shared/stores/problems/pagination";

const fetchTags = async (
   examName: string,
   sectionName: string
): Promise<Tag[]> => {
   const response = await fetch("/api/problems/getTags", {
      method: "POST",
      headers: {
         "Content-Type": "application/json",
      },
      body: JSON.stringify({
         examName,
         sectionName,
      }),
   });
   const tagData = response.json();
   return tagData;
};

export const useGetTags = () => {
   const { examName, sectionName } = usePaginationStore();

   const { status, data, error } = useQuery({
      queryKey: ["tags", examName, sectionName],
      queryFn: () => fetchTags(examName, sectionName),
      staleTime: 15 * 60 * 1000, // 15 minutes - tags rarely change

      refetchOnWindowFocus: false,
   });
   return {
      tagStatus: status,
      tagError: error,
      tagData: data,
   };
};
