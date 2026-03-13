export interface Tag {
   tagid: number;
   topic: string | null;
   theme: string | null;
   type: string | null;
   name?: string | null;
   examtypeid: number;
   sectionid: number;
   count: number; //number of questions with that tag
   isActive: boolean; //if that tag is selected by the user,
}
