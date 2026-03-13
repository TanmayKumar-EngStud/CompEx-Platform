import Link from 'next/link'
import { ButtonP } from '@/shared/components/ui/button'
import { Home, FileQuestion } from 'lucide-react'

export default function NotFound() {
    return (
        <div className="h-screen w-full flex flex-col items-center justify-center bg-background text-foreground space-y-4">
            <div className="p-4 bg-muted rounded-full">
                <FileQuestion className="w-12 h-12 text-muted-foreground" />
            </div>
            <h2 className="text-3xl font-bold">Page Not Found</h2>
            <p className="text-muted-foreground text-center max-w-md">
                We couldn&apos;t find the user or resource you were looking for. It might have been moved or deleted.
            </p>

            <Link href="/">
                <ButtonP className="flex items-center gap-2 mt-4">
                    <Home className="w-4 h-4" />
                    Return Home
                </ButtonP>
            </Link>
        </div>
    )
}
