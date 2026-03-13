/**
 * Enhanced fetchTags with priority-based caching
 * 
 * Implements intelligent tag fetching with priority levels:
 * 1. Current exam/section tags (immediate priority)
 * 2. Related section tags (high priority)
 * 3. Other exam tags (background priority)
 */

"use client";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo } from "react";
import { usePriorityCache, CachePriority } from "@/shared/lib/cache/priority-cache";

interface Tag {
  name: string;
  count: number;
  examName: string;
  sectionName: string;
}

interface TagsResponse {
  tags: Tag[];
  examName: string;
  sectionName: string;
}

interface TagsCacheState {
  [key: string]: TagsResponse; // key format: "examName-sectionName"
}

// Enhanced fetch function with priority awareness
const fetchTagsWithPriority = async (
  examName: string,
  sectionName: string,
  priority: CachePriority = CachePriority.IMMEDIATE
): Promise<TagsResponse> => {
  try {
    const response = await fetch(
      `/api/problems/tags?examName=${examName}&sectionName=${sectionName}`,
      {
        headers: {
          'X-Cache-Priority': priority.toString(),
        }
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch tags: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    
    return {
      tags: data.tags || [],
      examName,
      sectionName,
    };
  } catch (error) {
    console.error(`Error fetching tags for ${examName}/${sectionName}:`, error);
    throw error;
  }
};

// Hook for fetching tags with priority caching
export const useTagsWithPriority = (examName: string, sectionName: string) => {
  const queryClient = useQueryClient();
  const priorityCache = usePriorityCache();

  // Primary query for current exam/section tags
  const {
    data: currentTags,
    status,
    error,
    isLoading
  } = useQuery({
    queryKey: ["tags-priority", examName, sectionName],
    queryFn: () => fetchTagsWithPriority(examName, sectionName, CachePriority.IMMEDIATE),
    staleTime: 15 * 60 * 1000, // 15 minutes - tags don't change often
    refetchOnWindowFocus: false,
    enabled: !!examName && !!sectionName,
  });

  // Prefetch related section tags
  useEffect(() => {
    if (!examName || !sectionName || status !== 'success') return;

    const prefetchRelatedTags = async () => {
      // Get related sections within the same exam
      const relatedSections = getRelatedSections(examName, sectionName);
      
      // Prefetch related section tags with high priority
      const relatedPromises = relatedSections.map(section => 
        queryClient.prefetchQuery({
          queryKey: ["tags-priority", examName, section],
          queryFn: () => fetchTagsWithPriority(examName, section, CachePriority.HIGH),
          staleTime: 15 * 60 * 1000,
        })
      );

      // Prefetch other exam tags with lower priority
      const otherExams = getOtherExams(examName);
      const otherExamPromises = otherExams.flatMap(exam => 
        ['quants', 'verbal'].map(section =>
          queryClient.prefetchQuery({
            queryKey: ["tags-priority", exam, section],
            queryFn: () => fetchTagsWithPriority(exam, section, CachePriority.MEDIUM),
            staleTime: 30 * 60 * 1000, // Longer stale time for background data
          })
        )
      );

      // Execute high priority prefetches first
      await Promise.allSettled(relatedPromises);
      
      // Then execute background prefetches
      setTimeout(() => {
        Promise.allSettled(otherExamPromises).catch(error => 
          console.warn('Background tag prefetching failed:', error)
        );
      }, 1000); // Delay background fetching
    };

    prefetchRelatedTags();
  }, [examName, sectionName, status, queryClient]);

  return {
    tags: currentTags?.tags || [],
    status,
    error,
    isLoading,
    examName: currentTags?.examName || examName,
    sectionName: currentTags?.sectionName || sectionName,
  };
};

// Hook for getting cached tags from multiple exams/sections
export const useMultipleTagsCache = (examName: string, sectionName: string) => {
  const queryClient = useQueryClient();
  
  const getAllCachedTags = useMemo(() => {
    const cachedTags: TagsCacheState = {};
    
    // Get all cached tag queries
    const allQueries = queryClient.getQueriesData({
      queryKey: ["tags-priority"],
    });

    allQueries.forEach(([queryKey, data]) => {
      if (Array.isArray(queryKey) && queryKey.length >= 3) {
        const [, exam, section] = queryKey;
        const key = `${exam}-${section}`;
        if (data) {
          cachedTags[key] = data as TagsResponse;
        }
      }
    });

    return cachedTags;
  }, [queryClient]);

  // Get tags for current context
  const currentTags = getAllCachedTags[`${examName}-${sectionName}`]?.tags || [];
  
  // Get related tags
  const relatedSections = getRelatedSections(examName, sectionName);
  const relatedTags = relatedSections.flatMap(section => 
    getAllCachedTags[`${examName}-${section}`]?.tags || []
  );

  // Get other exam tags
  const otherExams = getOtherExams(examName);
  const otherExamTags = otherExams.flatMap(exam => 
    ['quants', 'verbal'].flatMap(section => 
      getAllCachedTags[`${exam}-${section}`]?.tags || []
    )
  );

  return {
    currentTags,
    relatedTags,
    otherExamTags,
    allCachedTags: getAllCachedTags,
    totalCachedSections: Object.keys(getAllCachedTags).length,
  };
};

// Hook for preloading all tags in background
export const useTagsPreloader = () => {
  const queryClient = useQueryClient();
  const priorityCache = usePriorityCache();

  const preloadAllTags = async (currentExam?: string, currentSection?: string) => {
    const examSections = [
      { exam: 'GRE', sections: ['quants', 'verbal'] },
      { exam: 'GMAT', sections: ['quants', 'verbal'] },
      { exam: 'CAT', sections: ['quants', 'verbal', 'lrdi'] },
    ];

    const tasks = examSections.flatMap(({ exam, sections }) =>
      sections.map(section => ({
        exam,
        section,
        // Set priority based on current context
        priority: 
          exam === currentExam && section === currentSection ? CachePriority.IMMEDIATE :
          exam === currentExam ? CachePriority.HIGH :
          CachePriority.MEDIUM
      }))
    );

    // Sort tasks by priority
    tasks.sort((a, b) => a.priority - b.priority);

    // Execute tasks with appropriate timing
    let delay = 0;
    const promises = tasks.map(({ exam, section, priority }) => {
      const promise = new Promise(resolve => {
        setTimeout(() => {
          queryClient.prefetchQuery({
            queryKey: ["tags-priority", exam, section],
            queryFn: () => fetchTagsWithPriority(exam, section, priority),
            staleTime: priority === CachePriority.IMMEDIATE ? 15 * 60 * 1000 : 30 * 60 * 1000,
          }).then(resolve).catch(resolve); // Don't fail the entire operation on single failures
        }, delay);
      });

      // Increase delay for lower priority items
      delay += priority === CachePriority.IMMEDIATE ? 0 : 
               priority === CachePriority.HIGH ? 200 : 500;

      return promise;
    });

    return Promise.allSettled(promises);
  };

  return { preloadAllTags };
};

// Utility functions
function getRelatedSections(currentExam: string, currentSection: string): string[] {
  const examSections: Record<string, string[]> = {
    'GRE': ['quants', 'verbal'],
    'GMAT': ['quants', 'verbal'],
    'CAT': ['quants', 'verbal', 'lrdi']
  };

  return (examSections[currentExam] || []).filter(section => section !== currentSection);
}

function getOtherExams(currentExam: string): string[] {
  const allExams = ['GRE', 'GMAT', 'CAT'];
  return allExams.filter(exam => exam !== currentExam);
}

// Hook for comprehensive tag statistics
export const useTagsStats = (examName: string, sectionName: string) => {
  const { currentTags, relatedTags, otherExamTags, totalCachedSections } = 
    useMultipleTagsCache(examName, sectionName);

  const stats = useMemo(() => {
    const currentCount = currentTags.length;
    const relatedCount = relatedTags.length;
    const otherCount = otherExamTags.length;
    const totalTags = currentCount + relatedCount + otherCount;

    // Calculate tag coverage
    const expectedSections = 7; // GRE(2) + GMAT(2) + CAT(3)
    const cacheCompleteness = (totalCachedSections / expectedSections) * 100;

    // Most common tags across all cached data
    const allTags = [...currentTags, ...relatedTags, ...otherExamTags];
    const tagFrequency = allTags.reduce((acc, tag) => {
      acc[tag.name] = (acc[tag.name] || 0) + tag.count;
      return acc;
    }, {} as Record<string, number>);

    const topTags = Object.entries(tagFrequency)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 10)
      .map(([name, count]) => ({ name, count }));

    return {
      currentCount,
      relatedCount,
      otherCount,
      totalTags,
      totalCachedSections,
      cacheCompleteness: Math.round(cacheCompleteness),
      topTags,
    };
  }, [currentTags, relatedTags, otherExamTags, totalCachedSections]);

  return stats;
};

// Legacy exports for backward compatibility
export { useTagsWithPriority as useTags };
export { fetchTagsWithPriority as fetchTags };