import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { loginSchema, type LoginInput } from '@verdin/validation';
import { Button, Card, CardContent, ErrorState, FormField, Input } from '@verdin/ui';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../lib/auth';
import { APP_NAME } from '@verdin/shared';

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginInput>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginInput) => {
    setError(null);
    try {
      await login(data.email, data.password);
      navigate('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <Card className="w-full max-w-md">
        <CardContent className="p-8">
          <h1 className="text-2xl font-bold text-gray-900">{APP_NAME}</h1>
          <p className="mt-1 text-sm text-gray-500">Sign in to your account</p>

          <form onSubmit={handleSubmit(onSubmit)} className="mt-8 space-y-4">
            <FormField label="Email" htmlFor="email" error={errors.email?.message} required>
              <Input id="email" type="email" hasError={!!errors.email} {...register('email')} />
            </FormField>

            <FormField
              label="Password"
              htmlFor="password"
              error={errors.password?.message}
              required
            >
              <Input
                id="password"
                type="password"
                hasError={!!errors.password}
                {...register('password')}
              />
            </FormField>

            {error ? <ErrorState title="Sign in failed" message={error} /> : null}

            <Button type="submit" loading={isSubmitting} className="w-full">
              Sign in
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
