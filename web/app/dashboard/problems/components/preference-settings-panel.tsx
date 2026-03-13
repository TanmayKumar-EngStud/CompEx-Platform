import React from "react";
import { Switch } from "@/shared/components/ui/switch";
import { Shuffle, Dice5 } from "lucide-react";
import { usePaginationCacheStore } from "@/features/question-solving/stores/pagination-cache.store";
import uiStrings from "../config/ui-strings.json";

interface PreferenceSettingsPanelProps {
   bookmarksEnabled: boolean;
   setBookmarksEnabled: (enabled: boolean) => void;

   showTimer: boolean;
   setShowTimer: React.Dispatch<React.SetStateAction<boolean>>;

   showDifficulty: boolean;
   setShowDifficulty: React.Dispatch<React.SetStateAction<boolean>>;

   questionTagsEnabled: boolean;
   setQuestionTagsEnabled: (enabled: boolean) => void;

   onShuffle: (sectionId?: string) => void;
}

/**
 * PreferenceSettingsPanel Component
 *
 * A reusable settings panel component that provides user preference controls
 * for the problems page, including toggles for bookmarks, timer, difficulty display,
 * and a shuffle functionality for problem ordering.
 *
 * @param props - Component props containing state and handlers for all settings
 * @returns JSX element containing the preference settings panel
 */
export function PreferenceSettingsPanel({
   bookmarksEnabled,
   setBookmarksEnabled,
   showTimer,
   setShowTimer,
   showDifficulty,
   setShowDifficulty,
   questionTagsEnabled,
   setQuestionTagsEnabled,
   onShuffle,
}: PreferenceSettingsPanelProps) {
   const { isShuffling, shuffleQuestions } = usePaginationCacheStore();

   const handleShuffle = async () => {
      try {
         console.log('🎲 Attempting to shuffle questions...');
         // Try using the cache service first, fall back to the original shuffle
         const success = await shuffleQuestions();
         if (success) {
            console.log('✅ Questions shuffled successfully using cache service');
         } else {
            console.log('⚠️ Cache service shuffle failed, falling back to original method');
            // Fall back to the original shuffle method
            onShuffle();
         }
      } catch (error) {
         console.error('❌ Shuffle error:', error);
         // Fall back to the original shuffle method on error
         onShuffle();
      }
   };
   return (
      <section
         className="flex flex-col gap-4 mt-5"
         role="region"
         aria-labelledby="preference-settings-heading"
         data-testid="preference-settings-panel"
      >
         <h1
            id="preference-settings-heading"
            className="text-2xl tracking-tight mb-4"
         >
            {uiStrings.headers.preferenceSettings}
         </h1>

         <div
            className="flex justify-between gap-4 items-center"
            data-testid="bookmarks-setting"
         >
            <label
               htmlFor="bookmarks-switch"
               className="text-foreground cursor-pointer"
            >
               {uiStrings.labels.enableBookmarks}
            </label>
            <Switch
               id="bookmarks-switch"
               checked={bookmarksEnabled}
               onCheckedChange={() => {
                  setBookmarksEnabled(!bookmarksEnabled);
               }}
               aria-label={`${bookmarksEnabled ? "Disable" : "Enable"
                  } bookmarks functionality`}
               data-testid="bookmarks-switch"
            />
         </div>

         <div
            className="flex justify-between gap-4 items-center"
            data-testid="timer-setting"
         >
            <label
               htmlFor="timer-switch"
               className="text-foreground cursor-pointer"
            >
               {uiStrings.labels.showTimer}
            </label>
            <Switch
               id="timer-switch"
               checked={showTimer}
               onCheckedChange={() => {
                  setShowTimer(!showTimer);
               }}
               aria-label={`${showTimer ? "Hide" : "Show"
                  } timer during questions`}
               data-testid="timer-switch"
            />
         </div>

         <div
            className="flex justify-between gap-4 items-center"
            data-testid="difficulty-setting"
         >
            <label
               htmlFor="difficulty-switch"
               className="text-foreground cursor-pointer"
            >
               {uiStrings.labels.showDifficulty}
            </label>
            <Switch
               id="difficulty-switch"
               checked={showDifficulty}
               onCheckedChange={() => {
                  setShowDifficulty(!showDifficulty);
               }}
               aria-label={`${showDifficulty ? "Hide" : "Show"
                  } difficulty level for questions`}
               data-testid="difficulty-switch"
            />
         </div>

         <div
            className="flex justify-between gap-4 items-center"
            data-testid="question-tags-setting"
         >
            <label
               htmlFor="question-tags-switch"
               className="text-foreground cursor-pointer"
            >
               {uiStrings.labels.showQuestionTags}
            </label>
            <Switch
               id="question-tags-switch"
               checked={questionTagsEnabled}
               onCheckedChange={() => {
                  setQuestionTagsEnabled(!questionTagsEnabled);
               }}
               aria-label={`${questionTagsEnabled ? "Hide" : "Show"
                  } question tags in question window`}
               data-testid="question-tags-switch"
            />
         </div>

         <div
            className="flex justify-between gap-4 items-center"
            data-testid="shuffle-setting"
         >
            <span className="text-foreground">
               {uiStrings.labels.shuffleQuestions}
            </span>
            <button
               onClick={handleShuffle}
               disabled={isShuffling}
               className="p-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 disabled:bg-primary/50 disabled:cursor-not-allowed transition-colors duration-200 flex items-center gap-2 focus:ring-2 focus:ring-primary/50 focus:outline-none"
               title={uiStrings.messages.shuffleTooltip}
               aria-label="Shuffle the order of questions randomly"
               data-testid="shuffle-button"
            >
               <Dice5
                  size={16}
                  aria-hidden="true"
                  className={isShuffling ? "animate-spin" : ""}
               />
               <span className="text-sm">
                  {isShuffling ? "Shuffling..." : uiStrings.buttons.shuffle}
               </span>
            </button>
         </div>
      </section>
   );
}
