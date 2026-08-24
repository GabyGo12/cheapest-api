import { IsOptional, IsString, MaxLength } from 'class-validator';

export class UpdateTiendaDto {
  @IsOptional()
  @IsString()
  @MaxLength(255)
  nombreComercial?: string;

  @IsOptional()
  @IsString()
  @MaxLength(50)
  rut?: string;
}